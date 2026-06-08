# Evidencias — Generacion y carga

Evidencia de la carga de los datos sinteticos al Lakehouse fuente de Fabric.

## Contenido

| Archivo | Descripcion |
|---|---|
| `count_por_tabla.png` | Resultado de `SELECT COUNT(*)` por tabla en Fabric |
| `tablas_creadas.png` | Arbol de tablas Delta del Lakehouse |
| `reporte_generacion.json` | Reporte de la generacion local |
| `anomalias_inyectadas.json` | IDs afectados por cada anomalia |

## COUNT(*) por tabla

Lakehouse `lakehouse_retailmax_fuente`, workspace `RetailMax-Lab-DataKnow`:

| Tabla | Filas |
|---|---:|
| `mstr_proveedores` | 800 |
| `mstr_tiendas` | 150 |
| `mstr_articulos` | 5.000 |
| `crm_miembros` | 50.000 |
| `trans_ventas` | 1.001.000 |
| `inv_stock_diario` | 750.000 |
| `post_devoluciones` | 50.000 |

`trans_ventas` incluye 1.000 duplicados inyectados como anomalia; se eliminan
en la deduplicacion de la capa Silver.

## Flujo

```
Generacion local (Python)
  -> output/*.parquet
  -> Files/archivos_parquet/ (Lakehouse)
  -> Tables/* (Delta) via cargar_fuente_a_tablas
  -> SQL Analytics Endpoint
```
