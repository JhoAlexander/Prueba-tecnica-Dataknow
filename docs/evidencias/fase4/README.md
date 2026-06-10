# Evidencias — Orquestacion

Capturas y artefactos de la ejecucion del pipeline orquestado.

| Archivo | Descripcion |
|---|---|
| `dag_exitoso.png` | DAG con las 5 capas + Reporte_Exito en verde (Pipeline Succeeded) |
| `dag_fallo.png` | DAG con Bronze en rojo y Alerta_Fallo disparada (prueba de fallo) |
| `correo_exito.png` | Correo de reporte de exito recibido |
| `correo_alerta.png` | Correo de alerta de fallo recibido |
| `monitor_historial.png` | Monitor Hub con el historial de ejecuciones (>= 2) |
| `Schedule.png` | Configuracion de la ejecucion programada diaria a las 02:00 |

La definicion del DAG (como codigo) esta en
`orchestration/pipelines-export/pl_orquestacion_medallon.json`.

## Evidencia de reintentos

En la ejecucion de prueba (con un fallo forzado en Bronze), el Monitor mostro la
actividad Bronze ejecutada **4 veces** (1 intento original + 3 reintentos),
confirmando la politica `retry = 3`.
