"""Alerta de anomalia de volumen.

Compara el volumen procesado en la ultima ejecucion contra el promedio de las
ultimas 7 ejecuciones (segun la tabla de control _log_ingesta de Bronze). Si la
desviacion supera el 30%, registra una alerta en _alertas_volumen.


"""
from pyspark.sql import functions as F
from pyspark.sql import Window

# ===================== CONFIG =====================
_ONELAKE = "onelake.dfs.fabric.microsoft.com"
WS_DEV  = "60259c60-ec61-406c-94c9-305e41badf4c"
LH_BRONZE = "5d469c7d-d1b6-4166-89df-3caa8b8e6dc1"

def _bronze(t): return f"abfss://{WS_DEV}@{_ONELAKE}/{LH_BRONZE}/Tables/{t}"
UMBRAL_PCT = 30.0
# ==================================================

# Volumen total por ejecucion (batch).
log = spark.read.format("delta").load(_bronze("_log_ingesta"))
por_ejecucion = (log.groupBy("batch_id")
    .agg(F.sum("registros").alias("volumen"),
         F.max("ts_ejecucion").alias("ts"))
    .orderBy(F.desc("ts")))

filas = por_ejecucion.collect()
print(f"Ejecuciones registradas: {len(filas)}")

if len(filas) < 2:
    print("Se necesita mas de una ejecucion para evaluar la anomalia de volumen.")
else:
    actual = filas[0]
    anteriores = filas[1:8]  # hasta 7 ejecuciones previas
    promedio = sum(r["volumen"] for r in anteriores) / len(anteriores)
    desviacion = 100.0 * (actual["volumen"] - promedio) / promedio if promedio else 0.0
    anomalia = abs(desviacion) > UMBRAL_PCT

    print(f"Volumen actual:     {actual['volumen']:,}")
    print(f"Promedio previo (n={len(anteriores)}): {promedio:,.0f}")
    print(f"Desviacion:         {desviacion:+.1f}%  (umbral +/-{UMBRAL_PCT}%)")
    print(f"Anomalia de volumen: {'SI' if anomalia else 'NO'}")

    # Persistir el resultado en la tabla de alertas.
    resultado = spark.createDataFrame([{
        "batch_id": actual["batch_id"],
        "volumen_actual": int(actual["volumen"]),
        "promedio_previo": float(round(promedio, 0)),
        "desviacion_pct": float(round(desviacion, 1)),
        "es_anomalia": bool(anomalia),
    }]).withColumn("_ts", F.current_timestamp())
    resultado.write.format("delta").mode("append").save(_bronze("_alertas_volumen"))

    # Demostracion: como se comportaria ante un volumen anomalo (mitad del promedio).
    vol_simulado = promedio * 0.5
    desv_simulada = 100.0 * (vol_simulado - promedio) / promedio
    print(f"\n[Demostracion] Con un volumen de {vol_simulado:,.0f} "
          f"(desviacion {desv_simulada:+.1f}%) -> "
          f"{'ALERTA' if abs(desv_simulada) > UMBRAL_PCT else 'sin alerta'}")
