# Evidencia — Capa Bronze

Ingesta cruda desde el lakehouse fuente con columnas de auditoria,
particionamiento por fecha de ingesta e idempotencia por MERGE.

```
Batch: c4ed9c61-72a9-49bd-a018-3e096b2cf41a | 2026-06-08 12:03:17 UTC-05:00 | incremental=True
  mstr_proveedores       ->       800 registros (18.8s)
  mstr_tiendas           ->       150 registros (5.2s)
  mstr_articulos         ->     5,000 registros (4.6s)
  crm_miembros           ->    50,000 registros (4.8s)
  trans_ventas           -> 1,001,000 registros (7.1s)
  inv_stock_diario       ->   750,000 registros (5.9s)
  post_devoluciones      ->    50,000 registros (4.4s)

Bronze completado: 1,856,950 registros en 7 tablas.
```

`trans_ventas` ingresa con 1.001.000 filas (incluye los 1.000 duplicados
anomalos que se eliminan en Silver). Cada registro lleva las columnas de
auditoria `_ts_ingesta`, `_sistema_fuente` y `_batch_id`.
