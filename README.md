# Pipeline de Datos End-to-End — Sector Retail (RetailMax)

Pipeline analitico completo para una cadena de retail con operacion en 5 paises
de LATAM: generacion de datos, arquitectura Medallion (Bronze/Silver/Gold),
orquestacion y gobierno de datos sobre Microsoft Fabric.

---

## 1. Sector y plataforma

### Sector: Retail y comercio electronico

**RetailMax**, cadena de consumo masivo con presencia fisica en Colombia, Mexico,
Chile, Peru y Ecuador (148 tiendas) y canal e-commerce.

Necesidades de negocio que resuelve el pipeline:
- Deteccion diaria de riesgo de quiebre de stock (cobertura < 7 dias)
- Segmentacion RFM de los miembros del programa de fidelizacion
- Tasa de conversion por canal y categoria
- Analisis de devoluciones por motivo, proveedor y canal
- Vista ejecutiva de ventas diarias por pais, tienda, canal y categoria

El modelo de datos (7 tablas con jerarquias de categoria, relaciones
producto-proveedor y hechos de ventas/inventario/devoluciones) permite
implementar una variedad amplia de reglas de negocio analiticas.

### Plataforma: Microsoft Fabric

| Criterio | Microsoft Fabric | Azure (servicios separados) |
|---|---|---|
| Costo | Trial F64 sin costo | 5 a 30 USD |
| Integracion | Lakehouse + Data Factory + Notebooks + Power BI nativos | ADLS + ADF + Databricks + Key Vault + Log Analytics |
| Storage | OneLake unificado (Bronze/Silver/Gold) | ADLS Gen2 manual |
| Curva de aprendizaje | Media | Alta |

Microsoft Fabric integra almacenamiento (OneLake), procesamiento (notebooks
PySpark), orquestacion (Data Factory) y visualizacion (Power BI) en un unico
workspace, lo que reduce la complejidad operativa y permite concentrar el
esfuerzo en la arquitectura Medallion, la calidad y el gobierno de datos.

---

## 2. Arquitectura

```
+------------+     +---------------+     +-------------------+     +-------------+
| Generador  |---->| Lakehouse     |---->| Lakehouse OneLake |---->| Power BI    |
| Python     |     | fuente (SQL   |     | Bronze/Silver/Gold|     | Dashboard   |
| (Faker)    |     | endpoint)     |     | (Delta Lake)      |     | ejecutivo   |
+------------+     +---------------+     +-------------------+     +-------------+
                          |                       |
                          |                       v
                          |          Fabric Data Pipelines (orquestacion)
                          |          + Data Activator (alertas)
                          +----------+ Gobierno (roles, PII, catalogo)
```

---

## 3. Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `/data-generation` | Generacion de datos sinteticos y carga al Lakehouse |
| `/infra` | Configuracion de la infraestructura en Fabric |
| `/pipelines` | Transformaciones Bronze, Silver y Gold |
| `/orchestration` | Definicion de los pipelines de orquestacion |
| `/docs` | Diagrama ER, catalogo, decisiones de diseno y evidencias |

---

## 4. Reproduccion

### Requisitos
- Python 3.11+
- Git
- Cuenta de Microsoft Fabric con capacidad (trial o F2+)

### Pasos

```powershell
# 1. Clonar
git clone https://github.com/JhoAlexander/Prueba-tecnica-Dataknow.git
Set-Location Prueba-tecnica-Dataknow

# 2. Entorno e instalacion
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Generar datos sinteticos (CSV + Parquet en data-generation/output/)
python data-generation/generador.py

# 4. Subir los Parquet al Lakehouse de Fabric y ejecutar el notebook
#    data-generation/cargar_fuente_a_tablas.py para registrarlos como
#    tablas Delta (ver docs/evidencias/fase1/).
```

---

## 5. Estado del proyecto

- [x] Generacion de datos sinteticos y carga al Lakehouse
- [ ] Infraestructura en Fabric
- [ ] Pipeline Medallion (Bronze, Silver, Gold)
- [ ] Orquestacion y alertas
- [ ] Gobierno, roles y catalogo

---

## 6. Decisiones de diseno

- **Formato de tabla:** Delta Lake (ACID, versionado, time travel) sobre Parquet
- **Generacion de datos:** Python + Faker, reproducible con semilla fija
- **Orquestacion:** Fabric Data Pipelines (integrado, sin servidor adicional)

---

## 7. Autor

Jhoany Alexander Alzate Suarez — [@JhoAlexander](https://github.com/JhoAlexander)
