# pipelines

Transformaciones de la arquitectura Medallion.

## Capas

**Bronze — ingesta cruda**
- Copia desde el Lakehouse fuente en formato Delta
- Esquema original sin modificaciones
- Columnas de auditoria (timestamp de ingesta, sistema fuente, batch)
- Particionamiento por fecha
- Ingesta incremental

**Silver — limpieza y conformidad**
- Deduplicacion y tipado
- Validacion de integridad referencial (registros invalidos a tabla de errores)
- Enmascaramiento de columnas PII
- Reporte de calidad por ejecucion

**Gold — modelo analitico**
- Dimensiones: productos, tiendas, clientes
- Hechos: ventas, inventario, devoluciones, RFM
- Vistas agregadas y tabla de KPIs

## Estructura prevista

```
bronze/        Ingesta
silver/        Limpieza, validacion, calidad
gold/          Reglas de negocio y agregaciones
common/        Utilidades compartidas
data_quality/  Verificaciones automatizadas
```

## Idempotencia

Las escrituras usan `MERGE` sobre Delta con llaves naturales, de modo que
reejecutar el pipeline no genera duplicados.
