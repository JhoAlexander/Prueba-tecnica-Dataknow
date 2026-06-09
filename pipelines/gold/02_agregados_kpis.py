"""Capa Gold (2/2) — Agregados y KPIs ejecutivos.

Construye vistas de agregacion para consumo analitico y una tabla de KPIs
ejecutivos lista para el dashboard.

"""
from pyspark.sql import functions as F
from pyspark.sql import Window

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_GOLD = "07875980-48ed-4203-95cc-c992a1e7e37a"

def _gold(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_GOLD}/Tables/{t}"
def leer(t):  return spark.read.format("delta").load(_gold(t))
def escribir(df, t):
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(_gold(t))
# ==================================================

fact_ventas = leer("fact_ventas")
dim_tiendas = leer("dim_tiendas").select("id_tienda", "id_pais", "zona_distribucion", "tipo_tienda_desc")
dim_productos = leer("dim_productos").select("art_id", "id_categ_n1", "categoria_n1")

# Ventas enriquecidas con pais (tienda) y categoria (producto).
ventas_enr = (fact_ventas
    .join(dim_tiendas, "id_tienda", "left")
    .join(dim_productos, "art_id", "left"))

# ---------- agg_ventas_diarias ----------
agg_ventas_diarias = (ventas_enr.groupBy(
        "fec_trans", "id_pais", "id_tienda", "canal_venta", "categoria_n1")
    .agg(F.round(F.sum("vr_venta_neto"), 2).alias("ventas_netas"),
         F.sum("qty_vendida").alias("unidades"),
         F.countDistinct("id_trans").alias("transacciones"),
         F.round(F.avg("vr_venta_neto"), 2).alias("ticket_promedio")))
escribir(agg_ventas_diarias, "agg_ventas_diarias")
print(f"  agg_ventas_diarias: {agg_ventas_diarias.count():,} filas")

# ---------- agg_tasa_devolucion (por categoria n1 y canal) ----------
vendidas = (ventas_enr.groupBy("categoria_n1", "canal_venta")
    .agg(F.sum("qty_vendida").alias("unidades_vendidas")))
fact_dev = leer("fact_devoluciones").join(dim_productos, "art_id", "left")
devueltas = (fact_dev.groupBy("categoria_n1", F.col("canal_devolucion").alias("canal_venta"))
    .agg(F.sum("qty_devuelta").alias("unidades_devueltas")))
agg_tasa_devolucion = (vendidas.join(devueltas, ["categoria_n1", "canal_venta"], "left")
    .fillna({"unidades_devueltas": 0})
    .withColumn("tasa_devolucion_pct", F.round(
        100.0 * F.col("unidades_devueltas") / F.col("unidades_vendidas"), 2)))
escribir(agg_tasa_devolucion, "agg_tasa_devolucion")
print(f"  agg_tasa_devolucion: {agg_tasa_devolucion.count():,} filas")

# ---------- agg_segmentos_rfm (distribucion para marketing) ----------
agg_segmentos_rfm = (leer("fact_rfm_clientes").groupBy("etiqueta")
    .agg(F.count("*").alias("clientes"),
         F.round(F.avg("monetario"), 2).alias("monetario_promedio"),
         F.round(F.avg("frecuencia"), 2).alias("frecuencia_promedio"))
    .orderBy(F.desc("clientes")))
escribir(agg_segmentos_rfm, "agg_segmentos_rfm")
print(f"  agg_segmentos_rfm: {agg_segmentos_rfm.count():,} filas")

# ---------- kpi_ventas_pais_canal ----------
kpi_pais_canal = (ventas_enr.groupBy("id_pais", "canal_venta")
    .agg(F.round(F.sum("vr_venta_neto"), 2).alias("ventas_netas"),
         F.sum("qty_vendida").alias("unidades"),
         F.countDistinct("id_trans").alias("transacciones"),
         F.round(F.avg("vr_venta_neto"), 2).alias("ticket_promedio"),
         F.round(100.0 * F.sum(F.when(F.col("ind_descuento"), 1).otherwise(0))
                 / F.count("*"), 2).alias("pct_con_descuento"))
    .orderBy("id_pais", "canal_venta"))
escribir(kpi_pais_canal, "kpi_ventas_pais_canal")
print(f"  kpi_ventas_pais_canal: {kpi_pais_canal.count():,} filas")

# ---------- kpi_top_productos (top 10 por categoria) ----------
ventas_prod = (ventas_enr.groupBy("art_id", "categoria_n1")
    .agg(F.round(F.sum("vr_venta_neto"), 2).alias("ventas_netas"),
         F.sum("qty_vendida").alias("unidades")))
kpi_top_productos = (ventas_prod
    .withColumn("rank", F.row_number().over(
        Window.partitionBy("categoria_n1").orderBy(F.desc("ventas_netas"))))
    .filter(F.col("rank") <= 10)
    .orderBy("categoria_n1", "rank"))
escribir(kpi_top_productos, "kpi_top_productos")
print(f"  kpi_top_productos: {kpi_top_productos.count():,} filas")

# ---------- kpi_ventas_semanales (comparativo vs semana anterior) ----------
sem = (ventas_enr
    .withColumn("anio", F.year("fec_trans"))
    .withColumn("semana", F.weekofyear("fec_trans"))
    .groupBy("id_pais", "anio", "semana")
    .agg(F.round(F.sum("vr_venta_neto"), 2).alias("ventas_netas")))
w = Window.partitionBy("id_pais").orderBy("anio", "semana")
kpi_ventas_semanales = (sem
    .withColumn("ventas_semana_anterior", F.lag("ventas_netas").over(w))
    .withColumn("variacion_pct", F.round(
        100.0 * (F.col("ventas_netas") - F.col("ventas_semana_anterior"))
        / F.col("ventas_semana_anterior"), 2))
    .orderBy("id_pais", "anio", "semana"))
escribir(kpi_ventas_semanales, "kpi_ventas_semanales")
print(f"  kpi_ventas_semanales: {kpi_ventas_semanales.count():,} filas")

print("\nGold (agregados y KPIs) completado.")
