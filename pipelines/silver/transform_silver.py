"""Capa Silver — Limpieza, validacion y conformidad.

Deduplica, valida integridad referencial (registros invalidos van a una tabla
de errores), detecta anomalias, enmascara PII y produce un reporte de calidad.
Idempotente: cada tabla destino se sobrescribe por completo en cada corrida.

"""
import time
from datetime import datetime, timezone, timedelta

from pyspark.sql import functions as F

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_BRONZE = "5d469c7d-d1b6-4166-89df-3caa8b8e6dc1"
LH_SILVER = "cca20c1b-8219-4641-88e0-16fc9cf3be56"

def _bronze(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_BRONZE}/Tables/{t}"
def _silver(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_SILVER}/Tables/{t}"

# Columnas de auditoria heredadas de Bronze (se recortan en Silver).
AUDIT = ["_ts_ingesta", "_sistema_fuente", "_batch_id",
         "_anio_ingesta", "_mes_ingesta", "_dia_ingesta"]

PK = {
    "mstr_proveedores": "id_proveedor", "mstr_tiendas": "id_tienda",
    "mstr_articulos": "art_id", "crm_miembros": "id_miembro",
    "trans_ventas": "id_trans", "inv_stock_diario": "id_snapshot",
    "post_devoluciones": "id_devolucion",
}

# (tabla, columna_fk, tabla_padre, columna_pk_padre)
FKS = [
    ("mstr_articulos",    "id_proveedor",    "mstr_proveedores"),
    ("trans_ventas",      "id_tienda",       "mstr_tiendas"),
    ("trans_ventas",      "art_id",          "mstr_articulos"),
    ("inv_stock_diario",  "art_id",          "mstr_articulos"),
    ("inv_stock_diario",  "id_tienda",       "mstr_tiendas"),
    ("post_devoluciones", "id_trans_origen", "trans_ventas"),
    ("post_devoluciones", "art_id",          "mstr_articulos"),
    ("post_devoluciones", "id_tienda",       "mstr_tiendas"),
]

PII = {"mstr_proveedores": ["razon_social"]}
CLAVE_NEGOCIO_VENTAS = ["id_miembro", "id_tienda", "art_id", "fec_trans", "hra_trans"]
TZ = timezone(timedelta(hours=-5))
HOY = datetime.now(TZ).date()
# ==================================================

errores = []   # acumulador de registros rechazados
reporte = []   # metricas de calidad por tabla
silver_dfs = {}  # tablas ya conformadas (para validar FKs)


def registrar_error(df_err, tabla, motivo, pk_col):
    """Acumula registros rechazados con su motivo."""
    if df_err is None or df_err.rdd.isEmpty():
        return 0
    n = df_err.count()
    e = (df_err.select(
            F.lit(tabla).alias("tabla_origen"),
            F.col(pk_col).cast("string").alias("id_registro"),
            F.lit(motivo).alias("motivo"),
            F.current_timestamp().alias("_ts_error"))
         )
    errores.append(e)
    return n


def procesar(tabla):
    t0 = time.time()
    pk = PK[tabla]
    df = spark.read.format("delta").load(_bronze(tabla)).drop(*AUDIT)
    n_entrada = df.count()

    # 1) Deduplicacion (filas identicas en columnas de negocio).
    df = df.dropDuplicates()
    # trans_ventas: ademas quita duplicados por clave de negocio (anomalia).
    if tabla == "trans_ventas":
        df = df.dropDuplicates(CLAVE_NEGOCIO_VENTAS)
    n_dedup = n_entrada - df.count()

    rechazados = 0

    # 2) Rechazo de PK nula.
    df_pk_nula = df.filter(F.col(pk).isNull())
    rechazados += registrar_error(df_pk_nula, tabla, "pk_nula", pk)
    df = df.filter(F.col(pk).isNotNull())

    # 3) Reglas de negocio especificas (anomalias de monto y fecha).
    if tabla == "trans_ventas":
        df_neg = df.filter(F.col("precio_unitario_venta") <= 0)
        rechazados += registrar_error(df_neg, tabla, "monto_no_positivo", pk)
        df = df.filter(F.col("precio_unitario_venta") > 0)

        df_fut = df.filter(F.col("fec_trans") > F.lit(HOY))
        rechazados += registrar_error(df_fut, tabla, "fecha_futura", pk)
        df = df.filter(F.col("fec_trans") <= F.lit(HOY))

    # 4) Integridad referencial contra las dimensiones ya conformadas.
    for (t, fk, padre) in FKS:
        if t != tabla:
            continue
        padre_pk = PK[padre]
        padre_ids = silver_dfs[padre].select(F.col(padre_pk).alias("_pid"))
        cond = F.col(fk) == F.col("_pid")
        # id_miembro NULL es valido (cliente anonimo): se excluye de la validacion.
        df_check = df.filter(F.col(fk).isNotNull()) if fk == "id_miembro" else df
        huerfanos = df_check.join(padre_ids, cond, "left_anti")
        rechazados += registrar_error(huerfanos, tabla, f"fk_invalida_{fk}", pk)
        validos_ids = df_check.join(padre_ids, cond, "left_semi").select(pk)
        if fk == "id_miembro":
            df = df.filter(F.col(fk).isNull()).unionByName(
                df.join(validos_ids, pk, "left_semi"))
        else:
            df = df.join(validos_ids, pk, "left_semi")

    # 5) Enmascaramiento de PII (hash SHA-256).
    for col in PII.get(tabla, []):
        df = df.withColumn(col, F.sha2(F.col(col).cast("string"), 256))

    # 6) Marca de procesamiento Silver.
    df = df.withColumn("_ts_silver", F.current_timestamp())
    n_salida = df.count()

    df.write.format("delta").mode("overwrite") \
      .option("overwriteSchema", "true").save(_silver(tabla))
    silver_dfs[tabla] = df

    reporte.append({
        "tabla": tabla, "entrada": n_entrada, "duplicados": n_dedup,
        "rechazados": rechazados, "salida": n_salida,
        "pct_conformes": round(100.0 * n_salida / n_entrada, 2) if n_entrada else 0.0,
    })
    print(f"  {tabla:22s} entrada={n_entrada:>9,} dedup={n_dedup:>5} "
          f"rechazados={rechazados:>4} salida={n_salida:>9,}")
    return time.time() - t0


# ===================== EJECUCION =====================
# Dimensiones primero, luego hechos (para validar FKs contra dimensiones).
ORDEN = ["mstr_proveedores", "mstr_tiendas", "mstr_articulos", "crm_miembros",
         "trans_ventas", "inv_stock_diario", "post_devoluciones"]

print(f"Silver | fecha de corte: {HOY}")
for tabla in ORDEN:
    procesar(tabla)

# Tabla de errores consolidada.
if errores:
    from functools import reduce
    df_err = reduce(lambda a, b: a.unionByName(b), errores)
    df_err.write.format("delta").mode("overwrite").save(_silver("_errores"))
    print(f"\nTabla de errores: {df_err.count()} registros rechazados")
    df_err.groupBy("tabla_origen", "motivo").count().orderBy("tabla_origen").show(truncate=False)

# Reporte de calidad.
rep_df = spark.createDataFrame(reporte).withColumn("_ts_reporte", F.current_timestamp())
rep_df.write.format("delta").mode("overwrite").save(_silver("_reporte_calidad"))
print("Reporte de calidad:")
rep_df.select("tabla", "entrada", "duplicados", "rechazados", "salida", "pct_conformes").show(truncate=False)
