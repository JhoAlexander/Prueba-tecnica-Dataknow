# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Unreleased]

### Added — Capa de consumo (BI)
- Dimension de calendario (`pipelines/gold/03_dim_calendario.py`): tabla de fechas
  continua que habilita la inteligencia de tiempo del modelo semantico.
- Modelo semantico en Direct Lake sobre Gold con esquema en estrella (`fact_ventas`
  mas dim_tiendas/productos/clientes/calendario) y nueve medidas DAX.
- Dashboard ejecutivo en Power BI: KPIs (ventas netas, variacion vs el mismo dia de
  la semana anterior, tasa de descuento promedio, ticket promedio), ventas por pais
  y canal, tendencia diaria, top 10 de articulos por categoria y tasa de descuento
  por categoria.
- Diseno, modelo, medidas y notas de implementacion en `docs/dashboard_ejecutivo.md`.

### Changed
- `fact_ventas.fec_trans` se almacena como `date` (antes `timestamp`) para poder
  relacionarla con la dimension de calendario; la hora permanece en `hra_trans`.

### Added — Documentacion final
- Diagrama de arquitectura end-to-end (`docs/arquitectura.md`, Mermaid).
- Registro de decisiones tecnicas con justificacion (`docs/decisiones_tecnicas.md`).
- README con guia de despliegue reproducible de las cinco fases e indice de docs.

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

### Added — Gobierno, seguridad y calidad
- Definicion de tres roles (Administrador, Ingeniero, Analista) con minimo
  privilegio: el Analista accede solo a la capa Gold (`docs/roles.md`).
- Catalogo de datos de Silver y Gold autogenerado (`docs/catalogo.md`,
  `docs/gen_catalogo.py`).
- Alerta de anomalia de volumen (`pipelines/data_quality/alerta_anomalia_volumen.py`):
  desviacion > 30% vs el promedio de las ultimas 7 ejecuciones.
- Enmascaramiento de PII por hash desde Silver y auditoria de accesos nativa de
  Fabric documentadas.

### Added — Orquestacion
- Fabric Data Pipeline (`pl_orquestacion_medallon`) que encadena los 5 notebooks
  del Medallion con dependencias on-success, reintentos (3) y timeouts por tarea.
- Programacion diaria a las 02:00 (America/Bogota).
- Notificaciones por correo: reporte de exito (on-success) y alerta de fallo
  (on-failure), via Office 365 Outlook.
- Definicion del DAG exportada en `orchestration/pipelines-export/`.
- Diseno y hallazgos documentados en `orchestration/diseno_orquestacion.md`
  (buzon Exchange para el conector de correo; logica AND de dependencias
  multiples y patron de alerta por actividad).

### Added — Pipeline Medallion
- Capa Bronze (`pipelines/bronze`): ingesta cruda con auditoria,
  particionamiento por fecha de ingesta, idempotencia por MERGE y log.
- Capa Silver (`pipelines/silver`): deduplicacion, validacion de integridad
  referencial con tabla de errores, deteccion de anomalias, enmascaramiento
  de PII y reporte de calidad.
- Capa Gold (`pipelines/gold`): dimensiones y hechos con reglas de negocio
  (vr_venta_neto, cobertura/alerta de quiebre, RFM), agregados y KPIs ejecutivos.
- Verificaciones de calidad (`pipelines/data_quality`): 8 validaciones, 8/8 PASS.
- Documento de linaje (`docs/linaje.md`) y evidencias en `docs/evidencias/fase3/`.

### Added — Infraestructura como Codigo
- Codigo Terraform en `infra/` con el provider de Microsoft Fabric: workspace,
  lakehouses Medallion (bronze/silver/gold) y asignaciones de rol parametrizadas.
- Configuracion multi-entorno (`environments/dev.tfvars`, `prod.tfvars`).
- Estado remoto en HCP Terraform (ejecucion local con Azure CLI).
- Evidencias de despliegue en `docs/evidencias/fase2/`.

### Notes
- `trans_ventas` contiene 1.001.000 filas (1.000.000 + 1.000 duplicados
  inyectados como anomalia para validar la deduplicacion en Silver).
- El entorno dev se despliega con Terraform; el entorno prod existe en Fabric
  y `prod.tfvars` documenta su parametrizacion equivalente.
