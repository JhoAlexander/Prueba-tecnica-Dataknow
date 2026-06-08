# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Unreleased]

### Added
- Configuracion centralizada de generacion (`config.yaml`): semilla, rango
  temporal, volumenes, paises, categorias, estacionalidad y anomalias.
- Definicion de las 7 tablas fuente en `schemas.py` con tipos, marca de PII
  y generador de DDL.
- Generadores por tabla (proveedores, tiendas, articulos, miembros, ventas,
  inventario, devoluciones) con integridad referencial.
- Inyeccion de anomalias controladas (`anomalias.py`): duplicados, fechas fuera
  de rango, montos negativos y referencias huerfanas.
- Orquestador `generador.py`: ~1.86M filas en CSV y Parquet con reporte de ejecucion.
- Diagrama ER en Mermaid autogenerado (`docs/er_diagram.md`).
- Notebook de carga a tablas Delta en el Lakehouse de Fabric.
- Evidencias de carga (COUNT por tabla, arbol de tablas) en `docs/evidencias/`.

### Notes
- `trans_ventas` contiene 1.001.000 filas (1.000.000 + 1.000 duplicados
  inyectados como anomalia para validar la deduplicacion en Silver).
