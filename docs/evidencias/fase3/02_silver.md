# Evidencia — Capa Silver

Deduplicacion, validacion de integridad referencial, deteccion de anomalias,
enmascaramiento de PII y reporte de calidad.

## Procesamiento por tabla

```
  mstr_proveedores  entrada=    800 dedup=  0 rechazados=  0 salida=    800
  mstr_tiendas      entrada=    150 dedup=  0 rechazados=  0 salida=    150
  mstr_articulos    entrada=  5,000 dedup=  0 rechazados=  0 salida=  5,000
  crm_miembros      entrada= 50,000 dedup=  0 rechazados=  0 salida= 50,000
  trans_ventas      entrada=1,001,000 dedup=1000 rechazados= 99 salida= 999,901
  inv_stock_diario  entrada= 750,000 dedup=  0 rechazados=  0 salida= 750,000
  post_devoluciones entrada= 50,000 dedup=  0 rechazados=  2 salida= 49,998
```

## Tabla de errores (101 registros rechazados)

| tabla_origen | motivo | count |
|---|---|---:|
| post_devoluciones | fk_invalida_id_trans_origen | 2 |
| trans_ventas | monto_no_positivo | 29 |
| trans_ventas | fk_invalida_art_id | 20 |
| trans_ventas | fecha_futura | 50 |

Las cuatro anomalias inyectadas en Fase 1 son detectadas:
- **1.000 duplicados** -> eliminados por deduplicacion (clave de negocio).
- **50 fechas futuras** -> rechazadas (`fecha_futura`).
- **30 montos negativos** -> 29 rechazados (`monto_no_positivo`); 1 coincidio
  con un duplicado ya eliminado.
- **20 FK huerfanas** (`art_id=99999`) -> rechazadas (`fk_invalida_art_id`).

Ademas, 2 devoluciones quedaron huerfanas al rechazarse su venta de origen
(integridad referencial en cascada).

## Reporte de calidad

| tabla | entrada | duplicados | rechazados | salida | pct_conformes |
|---|---:|---:|---:|---:|---:|
| mstr_proveedores | 800 | 0 | 0 | 800 | 100.0 |
| mstr_tiendas | 150 | 0 | 0 | 150 | 100.0 |
| mstr_articulos | 5000 | 0 | 0 | 5000 | 100.0 |
| crm_miembros | 50000 | 0 | 0 | 50000 | 100.0 |
| trans_ventas | 1001000 | 1000 | 99 | 999901 | 99.89 |
| inv_stock_diario | 750000 | 0 | 0 | 750000 | 100.0 |
| post_devoluciones | 50000 | 0 | 2 | 49998 | 100.0 |

PII: `razon_social` se almacena como hash SHA-256 desde Silver.
