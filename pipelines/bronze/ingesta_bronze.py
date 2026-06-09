"""Capa Bronze — Ingesta cruda desde el lakehouse fuente.

Copia las tablas fuente a Bronze sin transformar el esquema, agrega columnas
de auditoria, particiona por fecha de ingesta y soporta modo incremental.
Idempotente mediante MERGE por llave primaria.

"""
import time
import uuid
from datetime import datetime, timezone, timedelta

from pyspark.sql import functions as F
from delta.tables import DeltaTable

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_PROD = "ef3f34e4-d275-4635-923d-151c027f3261"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_FUENTE = "551056c6-6b7c-49d5-963c-f009cda2a170"
LH_BRONZE = "5d469c7d-d1b6-4166-89df-3caa8b8e6dc1"

# La fuente tiene schemas habilitados: las tablas viven bajo el schema dbo.
def _fuente(t): return f"abfss://{WS_PROD}@{_ONELAKE}/{LH_FUENTE}/Tables/dbo/{t}"
def _bronze(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_BRONZE}/Tables/{t}"

# Tabla -> (llave primaria, columna de fecha para watermark)
TABLAS = {
    "mstr_proveedores":  ("id_proveedor",  None),
    "mstr_tiendas":      ("id_tienda",     "fec_apertura"),
    "mstr_articulos":    ("art_id",        "fec_alta"),
    "crm_miembros":      ("id_miembro",    "fec_registro"),
    "trans_ventas":      ("id_trans",      "fec_trans"),
    "inv_stock_diario":  ("id_snapshot",   "fec_snapshot"),
    "post_devoluciones": ("id_devolucion", "fec_devolucion"),
}

SISTEMA_FUENTE = "lakehouse_retailmax_fuente"
INCREMENTAL = True   # False = recarga completa
TZ_BOGOTA = timezone(timedelta(hours=-5))
# ==================================================


def watermark_bronze(tabla, fecha_col):
    """Maxima fecha ya cargada en Bronze, o None si la tabla no existe."""
    if fecha_col is None or not DeltaTable.isDeltaTable(spark, _bronze(tabla)):
        return None
    row = spark.read.format("delta").load(_bronze(tabla)) \
        .agg(F.max(fecha_col).alias("m")).collect()[0]
    return row["m"]


def ingestar(tabla, pk, fecha_col, batch_id, ts_ingesta):
    t0 = time.time()
    df = spark.read.format("delta").load(_fuente(tabla))

    # Modo incremental: solo registros con fecha posterior al ultimo cargado.
    if INCREMENTAL and fecha_col is not None:
        wm = watermark_bronze(tabla, fecha_col)
        if wm is not None:
            df = df.filter(F.col(fecha_col) > F.lit(wm))

    # Columnas de auditoria y de particion (fecha de ingesta).
    df = (df
          .withColumn("_ts_ingesta", F.lit(ts_ingesta).cast("timestamp"))
          .withColumn("_sistema_fuente", F.lit(SISTEMA_FUENTE))
          .withColumn("_batch_id", F.lit(batch_id))
          .withColumn("_anio_ingesta", F.year("_ts_ingesta"))
          .withColumn("_mes_ingesta", F.month("_ts_ingesta"))
          .withColumn("_dia_ingesta", F.dayofmonth("_ts_ingesta")))

    n = df.count()

    if n > 0:
        if DeltaTable.isDeltaTable(spark, _bronze(tabla)):
            # MERGE por PK: actualiza existentes, inserta nuevos (idempotente).
            (DeltaTable.forPath(spark, _bronze(tabla)).alias("t")
             .merge(df.alias("s"), f"t.{pk} = s.{pk}")
             .whenMatchedUpdateAll()
             .whenNotMatchedInsertAll()
             .execute())
        else:
            (df.write.format("delta")
             .partitionBy("_anio_ingesta", "_mes_ingesta", "_dia_ingesta")
             .save(_bronze(tabla)))

    return {"tabla": tabla, "registros": n, "segundos": round(time.time() - t0, 1)}


# ===================== EJECUCION =====================
batch_id = str(uuid.uuid4())
ts_ingesta = datetime.now(TZ_BOGOTA)
print(f"Batch: {batch_id} | {ts_ingesta:%Y-%m-%d %H:%M:%S %Z} | incremental={INCREMENTAL}")

resultados = []
for tabla, (pk, fecha_col) in TABLAS.items():
    r = ingestar(tabla, pk, fecha_col, batch_id, ts_ingesta)
    resultados.append(r)
    print(f"  {tabla:22s} -> {r['registros']:>9,} registros ({r['segundos']}s)")

# Log de ejecucion en una tabla de control.
log_df = spark.createDataFrame([
    {**r, "batch_id": batch_id, "ts_ejecucion": ts_ingesta,
     "modo": "incremental" if INCREMENTAL else "full"}
    for r in resultados
])
log_df.write.format("delta").mode("append").save(_bronze("_log_ingesta"))

total = sum(r["registros"] for r in resultados)
print(f"\nBronze completado: {total:,} registros en {len(resultados)} tablas.")
