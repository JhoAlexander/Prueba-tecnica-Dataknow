

## 1. Sector y plataforma

### Sector: Retail y comercio electronico

**RetailMax**, cadena de consumo masivo con presencia fisica en Colombia, Mexico,
Chile, Peru y Ecuador (148 tiendas) y canal e-commerce.

Necesidades de negocio que resuelve el pipeline:
- Deteccion de riesgo de quiebre de stock (cobertura < 7 dias)
- Segmentacion RFM de los miembros del programa de fidelizacion
- Tasa de devolucion por categoria y canal
- Vista ejecutiva de ventas por pais, tienda, canal y categoria

### Plataforma: Microsoft Fabric

La escojo porque por costo puedo utilizar Trial F64 (gratis) y porque
integra almacenamiento, procesamiento PySpark, orquestacion y
visualizacion en un unico workspace, lo que me permite concentrar mas esfuerzo en la
arquitectura Medallon y lo importante del análisis de datos. Es una plataforma de facil entendimiento en mi opinión, mas que las otras.

También tengo bases de azure, pero tiene costo ya que no tengo usario pago.
Las otras plataformas nunca he trabajado en ellas.

---

## 2. Arquitectura

Diagrama completo en [docs/arquitectura.md](docs/arquitectura.md).

```
Generacion        Infra (Terraform)         Medallion (Fabric)        Consumo
  Python    -->   provisiona workspace -->  Bronze->Silver->Gold  -->  Power BI
  (Faker)         dev + lakehouses          (Delta Lake)               Analista (Gold)
     |                                            ^
     +--> Lakehouse fuente (origen) -------------+
                                            Data Pipeline (orquestacion 02:00 + alertas)
```

---

## 3. Estructura del repositorio

| Carpeta / archivo | Contenido |
|---|---|
| `data-generation/` | Generacion de datos sinteticos y carga al Lakehouse (Fase 1) |
| `infra/` | Terraform para el workspace y los lakehouses (Fase 2) |
| `pipelines/` | Transformaciones Bronze, Silver, Gold y calidad (Fase 3) |
| `orchestration/` | Definicion del Data Pipeline y diseno de la orquestacion (Fase 4) |
| `docs/` | Arquitectura, ER, catalogo, linaje, roles, decisiones, dashboard y evidencias |
| `CHANGELOG.md` | Historial de cambios |
| `requirements.txt` | Dependencias de Python |

Documentacion clave en `docs/`:
[arquitectura](docs/arquitectura.md) ·
[diagrama ER](docs/er_diagram.md) ·
[catalogo de datos](docs/catalogo.md) ·
[linaje](docs/linaje.md) ·
[roles y gobierno](docs/roles.md) ·
[decisiones tecnicas](docs/decisiones_tecnicas.md) ·
[dashboard ejecutivo](docs/dashboard_ejecutivo.md)

---

## 4. Guia de despliegue reproducible

### Requisitos
- Python 3.11+, Git, Terraform 1.8+, Azure CLI
- Cuenta de Microsoft Fabric con capacidad (trial o F2+)
- Cuenta de HCP Terraform (free) para el estado remoto

### Fase 1 — Datos sinteticos

```powershell
git clone https://github.com/JhoAlexander/Prueba-tecnica-Dataknow.git
Set-Location Prueba-tecnica-Dataknow

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Se genera 1.86M filas en data-generation/output/ (CSV + Parquet)
python data-generation/generador.py
```

Sube los `.parquet` a `Files/archivos_parquet/` de un lakehouse fuente en Fabric y
ejecuta el notebook `data-generation/cargar_fuente_a_tablas.py` para registrarlos
como tablas Delta.

### Fase 2 — Infraestructura (Terraform)

Investigué este tema apoyándome en la documentación oficial de Terraform y Fabric, ya que es nuevo para mí.

```powershell
az login --allow-no-subscriptions
Set-Location infra
Copy-Item terraform.tfvars.example terraform.tfvars   # completar tenant_id y capacity_id
terraform init
terraform apply -var-file="environments/dev.tfvars"
```

Crea el workspace dev y los lakehouses `lh_bronze`, `lh_silver`, `lh_gold`.
Detalle e ID de recursos en [infra/README.md](infra/README.md).

### Fase 3 — Pipeline Medallion

Se crea un notebook en Fabric por cada archivo y debo ejecutarlos en orden*

```
pipelines/bronze/ingesta_bronze.py
pipelines/silver/transform_silver.py
pipelines/gold/01_dimensiones_hechos.py
pipelines/gold/02_agregados_kpis.py
pipelines/data_quality/validaciones.py
```

### Fase 4 — Orquestacion

Importa o recrea el Data Pipeline desde
`orchestration/pipelines-export/pl_orquestacion_medallon.json`, que encadena los
notebooks con dependencias, reintentos, timeouts, alertas por correo y schedule
diario a las 02:00. Diseno en [orchestration/diseno_orquestacion.md](orchestration/diseno_orquestacion.md).

### Fase 5 — Gobierno

Asigna los roles (ver [docs/roles.md](docs/roles.md)) y comparte solo `lh_gold`
con el rol Analista. El catalogo se regenera con `python docs/gen_catalogo.py`.
Tuve problemas con la creación de un usuario, creé un externo con otra cuenta mia pero 
no verifiqué autentificación.

### Dashboard ejecutivo (Power BI)

1. Ejecuto `pipelines/gold/03_dim_calendario.py` para crear la dimension de
   calendario en `lh_gold`.
2. Creo un modelo semantico en Direct Lake sobre `lh_gold` con `fact_ventas` y las
   dimensiones; relacionalas en estrella y marca `dim_calendario` como tabla de fechas.
3. Creo las medidas DAX y construye el informe con las visualizaciones del dashboard.

Modelo, relaciones, medidas, layout y notas de implementacion en
[docs/dashboard_ejecutivo.md](docs/dashboard_ejecutivo.md).


## 5. Decisiones de diseño

Resumen; detalle en [docs/decisiones_tecnicas.md](docs/decisiones_tecnicas.md).

- **Formato de tabla:** Delta Lake (ACID, MERGE para idempotencia, time travel).
- **Generacion de datos:** Python + Faker, reproducible con semilla fija.
- **IaC:** Terraform con el provider oficial de Fabric; estado remoto en HCP Terraform.Aprendizaje ya que no he trabajdo con eso antes.
- **Orquestacion:** Fabric Data Pipelines (integrado, sin servidor adicional).
- **Dos entornos:** dev (Terraform) y prod (UI), parametrizados por `tfvars`.

---

## 6. Autor

Jhoany Alexander Alzate Suarez. Ingeniero Electrónico/IoT
 — [@JhoAlexander](https://github.com/JhoAlexander)
