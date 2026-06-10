# Diseno de la orquestacion

Orquestador: **Fabric Data Pipeline** (`pl_orquestacion_medallon`), en el
workspace dev.

## DAG y dependencias

```
Bronze ✓→ Silver ✓→ Gold_Dim_Hechos ✓→ Gold_Agregados ✓→ Data_Quality ✓→ Reporte_Exito
   ✗                                                          
   └──────────────────────────────────────────────────────> Alerta_Fallo
```

Cada actividad ejecuta uno de los notebooks del pipeline Medallion. Las flechas
**verdes** son dependencias *on-success*: una capa solo inicia cuando la anterior
finaliza con exito. Esto garantiza que Silver no procese datos que Bronze aun no
preparo.

| Actividad | Notebook |
|---|---|
| Bronze | 01_bronze_ingesta |
| Silver | 02_silver_transform |
| Gold_Dim_Hechos | 03_gold_dimensiones_hechos |
| Gold_Agregados | 04_gold_agregados_kpis |
| Data_Quality | 05_data_quality |

## Programacion (schedule)

Ejecucion automatica **diaria a las 02:00**, zona horaria **(UTC-05:00) America/Bogota**.

## Reintentos y timeouts

Cada actividad: **Retry = 3** con intervalo de 60 s, y un **timeout** acorde al
volumen (30 min para Bronze/Silver/Gold, 15-20 min para agregados y calidad).

> **Nota sobre el backoff exponencial:** la prueba sugiere reintentos con backoff
> exponencial. Fabric Data Pipeline solo admite **intervalo fijo** entre reintentos
> (limitacion de la herramienta). Un backoff exponencial real requeriria logica
> adicional (por ejemplo, `time.sleep` creciente dentro del notebook, o un
> orquestador como Airflow). Se opto por el reintento con intervalo fijo que la
> plataforma soporta de forma nativa.

## Notificaciones

Actividad **Office 365 Outlook** para correo:
- **Reporte_Exito** (*on-success* desde Data_Quality): confirma la ejecucion y
  apunta a las tablas de control con las metricas (`_log_ingesta`,
  `_reporte_calidad`, `_resultados_dq`).
- **Alerta_Fallo** (*on-failure*): notifica el fallo con la hora del trigger.

### Hallazgo: el conector de correo requiere buzon Exchange
El conector "Office 365 Outlook" solo funciona con cuentas **organizacionales con
buzon de Exchange Online**. La identidad del tenant de Fabric
(`...onmicrosoft.com`) no tiene buzon, y las cuentas personales (Outlook.com /
Hotmail) no son aceptadas por el conector. Se resolvio usando una cuenta de
correo con buzon valido. Es la diferencia entre una **identidad** (puede
autenticarse) y un **buzon** (puede enviar/recibir correo).

### Manejo de errores: dependencias AND y patron de alerta
En Fabric, cuando una actividad tiene **varias dependencias entrantes**, se
evaluan con logica **AND**: la actividad corre solo si **todas** se cumplen.
Por eso, conectar el *on-failure* de las 5 actividades a una unica `Alerta_Fallo`
hace que esta requiera que **las 5 fallen** a la vez, lo que casi nunca ocurre
(si Bronze falla, las siguientes ni arrancan).

El patron correcto para "alertar si **cualquier** tarea falla" (logica OR) es
**una actividad de alerta por tarea**: el *on-failure* de cada notebook apunta a
su propia alerta. La alerta quedo demostrada con la actividad Bronze; el mismo
patron se replica para las demas capas. Una alternativa mas compacta es envolver
el core en un **pipeline hijo** y, en el pipeline padre, una unica alerta sobre
el *on-failure* de la actividad "Invoke pipeline".

## Monitoreo

El **Monitor Hub** de Fabric registra cada ejecucion con su estado, duracion y
detalle por actividad, accesible sin abrir el codigo. El historial incluye al
menos una ejecucion exitosa y una fallida (prueba de la alerta).

## Evidencias

En `docs/evidencias/fase4/`: DAG exitoso, DAG con fallo, correos de exito y
alerta, e historial del Monitor Hub.
