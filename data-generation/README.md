# data-generation

Generacion de datos sinteticos del modelo RetailMax y carga al Lakehouse.

## Caracteristicas

- Reproducible mediante semilla fija (`config.yaml`)
- Distribuciones realistas: estacionalidad mensual, picos horarios, precios lognormales
- Integridad referencial entre hechos y dimensiones
- ~5% de nulos en campos no criticos
- Anomalias controladas para validar el pipeline
- Salida en CSV y Parquet

## Tablas y volumenes

| Tabla | Filas |
|---|---:|
| MSTR_PROVEEDORES | 800 |
| MSTR_TIENDAS | 150 |
| MSTR_ARTICULOS | 5.000 |
| CRM_MIEMBROS | 50.000 |
| TRANS_VENTAS | 1.000.000 |
| INV_STOCK_DIARIO | 750.000 |
| POST_DEVOLUCIONES | 50.000 |

## Archivos

```
config.yaml                 Parametros de generacion
schemas.py                  Definicion de tablas (columnas, tipos, PII, FKs)
auxiliares.py               Funciones compartidas
gen_01..07_*.py             Un generador por tabla
anomalias.py                Inyeccion de anomalias
generador.py                Orquestador
cargar_fuente_a_tablas.py   Carga a tablas Delta en Fabric (PySpark)
```

## Uso

```bash
python generador.py
```

Genera los archivos en `output/` (ignorado por git) y muestras en `muestras/`.
