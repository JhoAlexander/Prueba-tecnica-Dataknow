"""Verificaciones de calidad de datos sobre la capa Gold.

Validaciones personalizadas que comprueban unicidad de llaves, ausencia de
nulos criticos, integridad referencial, rangos de valores y consistencia de
los scores RFM. El resultado se guarda en una tabla de control.

"""
from pyspark.sql import functions as F

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_GOLD = "07875980-48ed-4203-95cc-c992a1e7e37a"

def _gold(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_GOLD}/Tables/{t}"
def leer(t):  return spark.read.format("delta").load(_gold(t))
# ==================================================

resultados = []
def check(nombre, descripcion, valor_obtenido, ok):
    estado = "PASS" if ok else "FAIL"
    resultados.append({"check": nombre, "descripcion": descripcion,
                       "valor_obtenido": str(valor_obtenido), "estado": estado})
    print(f"  [{estado}] {nombre}: {valor_obtenido}")

# 1) Unicidad de la llave primaria en las dimensiones.
for dim, pk in [("dim_productos", "art_id"), ("dim_tiendas", "id_tienda"),
                ("dim_clientes", "id_miembro")]:
    df = leer(dim)
    total, distintos = df.count(), df.select(pk).distinct().count()
    check(f"pk_unica_{dim}", f"{pk} sin duplicados",
          f"{total} filas / {distintos} {pk} distintos", total == distintos)

# 2) Ausencia de nulos en campos criticos de fact_ventas.
fv = leer("fact_ventas")
nulos = fv.filter(F.col("vr_venta_neto").isNull() | F.col("art_id").isNull()
                  | F.col("id_tienda").isNull()).count()
check("no_nulos_fact_ventas", "vr_venta_neto, art_id e id_tienda no nulos",
      f"{nulos} nulos", nulos == 0)

# 3) Integridad referencial: art_id de fact_ventas existe en dim_productos.
art_dim = leer("dim_productos").select("art_id")
huerfanos = fv.join(art_dim, "art_id", "left_anti").count()
check("ri_ventas_productos", "fact_ventas.art_id existe en dim_productos",
      f"{huerfanos} huerfanos", huerfanos == 0)

# 4) Rango valido: vr_venta_neto positivo (anomalias filtradas en Silver).
no_positivos = fv.filter(F.col("vr_venta_neto") <= 0).count()
check("rango_vr_venta_neto", "vr_venta_neto > 0",
      f"{no_positivos} no positivos", no_positivos == 0)

# 5) Scores RFM dentro del rango 1-5.
rfm = leer("fact_rfm_clientes")
fuera = rfm.filter(~F.col("R").between(1, 5) | ~F.col("F").between(1, 5)
                   | ~F.col("M").between(1, 5)).count()
check("rango_scores_rfm", "R, F y M entre 1 y 5",
      f"{fuera} fuera de rango", fuera == 0)

# 6) Consistencia: cobertura_dias no negativa en fact_inventario.
inv = leer("fact_inventario")
cob_neg = inv.filter(F.col("cobertura_dias") < 0).count()
check("rango_cobertura", "cobertura_dias >= 0 (o nula)",
      f"{cob_neg} negativas", cob_neg == 0)

# Resumen y persistencia.
df_res = spark.createDataFrame(resultados).withColumn("_ts", F.current_timestamp())
df_res.write.format("delta").mode("overwrite").save(_gold("_resultados_dq"))

total = len(resultados)
pasados = sum(1 for r in resultados if r["estado"] == "PASS")
print(f"\nResultado: {pasados}/{total} verificaciones PASS")
df_res.select("check", "estado", "valor_obtenido").show(truncate=False)
