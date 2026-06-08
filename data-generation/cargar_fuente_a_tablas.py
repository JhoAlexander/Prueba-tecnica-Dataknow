"""Carga de los Parquet a tablas Delta en el Lakehouse de Fabric.

Codigo de referencia del notebook PySpark de Fabric. Lee los archivos
de Files/archivos_parquet/ y los registra como tablas Delta managed.

Requiere el runtime Spark de Fabric con un Default Lakehouse asignado;
no se ejecuta en local.
"""

# --- Celda 1: entorno Spark con zona horaria Colombia ---
from pyspark.sql import SparkSession
import time

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "America/Bogota")

print(f"Spark version: {spark.version}")
print(f"Timezone: {spark.conf.get('spark.sql.session.timeZone')}")


# --- Celda 2: tablas y ruta fuente ---
TABLAS = [
    "mstr_proveedores",
    "mstr_tiendas",
    "mstr_articulos",
    "crm_miembros",
    "trans_ventas",
    "inv_stock_diario",
    "post_devoluciones",
]
RUTA_FUENTE = "Files/archivos_parquet"


# --- Celda 3: cargar Parquet -> Delta ---
resultados = []
for tabla in TABLAS:
    t0 = time.time()
    df = spark.read.parquet(f"{RUTA_FUENTE}/{tabla}.parquet")
    n_filas = df.count()
    df.write.mode("overwrite").format("delta").saveAsTable(tabla)
    elapsed = time.time() - t0
    resultados.append({"tabla": tabla, "filas": n_filas, "segundos": round(elapsed, 1)})
    print(f"[{elapsed:5.1f}s] {tabla:22s} -> {n_filas:>9,} filas")


# --- Celda 4: validacion COUNT(*) por tabla ---
spark.sql("SHOW TABLES").show(truncate=False)
for tabla in TABLAS:
    n = spark.sql(f"SELECT COUNT(*) AS conteo FROM {tabla}").collect()[0]["conteo"]
    print(f"{tabla:<22} {n:>12,}")


# --- Celda 5: vista previa ---
spark.sql("DESCRIBE trans_ventas").show(20, truncate=False)
spark.sql("SELECT * FROM trans_ventas LIMIT 5").show(truncate=False)


# --- Celda 6: metadata de auditoria con hora Colombia ---
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_BOGOTA = ZoneInfo("America/Bogota")
ahora_co = datetime.now(TZ_BOGOTA)

metadata_rows = [
    (r["tabla"], r["filas"], r["segundos"], ahora_co)
    for r in resultados
]
metadata_df = spark.createDataFrame(
    metadata_rows,
    ["tabla", "filas_cargadas", "segundos_carga", "fecha_carga"]
)
metadata_df.write.mode("overwrite").format("delta").saveAsTable("_metadata_carga_fuente")
metadata_df.show(truncate=False)
