# orchestration

Orquestacion del pipeline con Fabric Data Pipelines.

## Flujo

```
Trigger (programado / manual)
  -> Extraccion del Lakehouse fuente
  -> Bronze
  -> Silver
  -> Gold
  -> Verificaciones de calidad
  -> Notificacion (exito / fallo)
```

Las dependencias son explicitas: cada capa inicia solo cuando la anterior
finaliza con exito.

## Configuracion 

- Ejecucion programada diaria (02:00, America/Bogota)
- Reintentos con backoff exponencial
- Timeout por tarea segun volumen
- Alerta por correo ante fallo (DAG, tarea, hora, error)
- Reporte diario de ejecucion (registros por capa, tiempo, alertas)
- Alerta de anomalia de volumen (desviacion > 30% vs promedio reciente)

## Estructura prevista

```
pipelines-export/    Definiciones exportadas
schedules/           Configuracion de triggers
alerts/              Reglas de alerta
evidencias/          Capturas de ejecucion
```


