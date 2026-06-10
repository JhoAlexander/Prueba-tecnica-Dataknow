"""Capa Gold (3/3) — Dimension de calendario.

Tabla de fechas continua que cubre el rango de las ventas. Habilita la
inteligencia de tiempo del modelo semantico: el comparativo contra el mismo dia
de la semana anterior se resuelve con DATEADD sobre esta dimension.
"""
from pyspark.sql import functions as F

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_GOLD = "07875980-48ed-4203-95cc-c992a1e7e37a"

def _gold(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_GOLD}/Tables/{t}"
def leer(t):  return spark.read.format("delta").load(_gold(t))
def escribir(df, t):
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(_gold(t))
# ==================================================

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS  = ["domingo", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]

# Rango que cubre todas las ventas (sin huecos intermedios).
r = leer("fact_ventas").agg(
        F.min("fec_trans").alias("ini"),
        F.max("fec_trans").alias("fin")).collect()[0]
print(f"Rango de ventas: {r.ini} -> {r.fin}")

fechas = spark.sql(
    f"SELECT explode(sequence(to_date('{r.ini}'), to_date('{r.fin}'),"
    f" interval 1 day)) AS fecha")

mes_es = F.element_at(F.array(*[F.lit(m) for m in MESES]), F.col("mes"))
dia_es = F.element_at(F.array(*[F.lit(d) for d in DIAS]),  F.col("dia_semana"))

dim_calendario = (fechas
    .withColumn("anio",          F.year("fecha"))
    .withColumn("trimestre",     F.quarter("fecha"))
    .withColumn("mes",           F.month("fecha"))
    .withColumn("nombre_mes",    mes_es)
    .withColumn("dia",           F.dayofmonth("fecha"))
    .withColumn("dia_semana",    F.dayofweek("fecha"))        # 1=domingo ... 7=sabado
    .withColumn("nombre_dia",    dia_es)
    .withColumn("semana_anio",   F.weekofyear("fecha"))
    .withColumn("es_fin_semana", F.dayofweek("fecha").isin(1, 7)))

escribir(dim_calendario, "dim_calendario")
print(f"  dim_calendario: {dim_calendario.count():,} filas")
dim_calendario.orderBy("fecha").show(7, truncate=False)
