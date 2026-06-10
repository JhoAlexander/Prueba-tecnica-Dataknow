# Arquitectura de la solucion

Diagrama de extremo a extremo: desde la generacion de datos hasta el consumo
analitico, sobre Microsoft Fabric.

```mermaid
flowchart TB
    subgraph LOCAL["1. Generacion local (Python)"]
        GEN["generador.py + Faker<br/>1.86M filas, semilla fija"]
        OUT["Parquet / CSV<br/>+ anomalias"]
        GEN --> OUT
    end

    subgraph IAC["2. Infraestructura como Codigo"]
        TF["Terraform<br/>provider microsoft/fabric"]
        HCP["Estado remoto<br/>HCP Terraform"]
        TF -.estado.-> HCP
    end

    subgraph FABRIC["Microsoft Fabric (OneLake)"]
        direction TB
        subgraph PROD["Workspace prod"]
            FUENTE["lakehouse_retailmax_fuente<br/>7 tablas Delta (origen)"]
        end
        subgraph DEV["Workspace dev (provisionado por Terraform)"]
            BRONZE["lh_bronze<br/>ingesta cruda + auditoria"]
            SILVER["lh_silver<br/>limpieza, validacion, PII"]
            GOLD["lh_gold<br/>dim/fact + reglas + KPIs"]
            BRONZE --> SILVER --> GOLD
        end
        PIPE["Data Pipeline<br/>orquestacion diaria 02:00<br/>reintentos + alertas"]
    end

    subgraph CONSUMO["4. Consumo y gobierno"]
        PBI["Power BI (Direct Lake)<br/>Dashboard ejecutivo<br/>modelo estrella + medidas DAX"]
        ANALISTA["Rol Analista<br/>solo lectura de Gold"]
        MAIL["Alertas por correo<br/>exito / fallo / volumen"]
    end

    OUT -->|upload| FUENTE
    TF ==>|provisiona| DEV
    FUENTE -->|3. ingesta| BRONZE
    GOLD --> PBI
    GOLD --> ANALISTA
    PIPE -.coordina.-> BRONZE
    PIPE -.coordina.-> SILVER
    PIPE -.coordina.-> GOLD
    PIPE --> MAIL
```

## Flujo en palabras

1. **Generacion (local):** `generador.py` crea datos sinteticos reproducibles con
   distribuciones realistas y anomalias controladas; exporta a Parquet/CSV.
2. **Infraestructura (Terraform):** provisiona el workspace dev y los lakehouses
   Medallion; el estado vive en un backend remoto, nunca en el repositorio.
3. **Medallion (PySpark en Fabric):**
   - **Bronze** ingesta la fuente sin transformar, con auditoria e idempotencia.
   - **Silver** deduplica, valida integridad, enmascara PII y reporta calidad.
   - **Gold** aplica las reglas de negocio y construye el modelo dimensional y los KPIs.
4. **Orquestacion:** un Data Pipeline encadena las capas con dependencias,
   reintentos y notificaciones, programado a las 02:00.
5. **Consumo y gobierno:** Gold alimenta un modelo semantico en Direct Lake sobre el
   que se construye el dashboard ejecutivo en Power BI (KPIs, comparativo vs el mismo
   dia de la semana anterior, top 10 por categoria y tasa de descuento); el rol
   Analista accede solo a Gold (minimo privilegio); las alertas llegan por correo.

## Decisiones de arquitectura destacadas

- **Dos workspaces:** prod (fuente con datos) y dev (Medallion, provisionado por
  IaC). Bronze lee la fuente entre workspaces (lectura cross-workspace), el resto
  fluye dentro de dev. Esto separa el origen operacional del entorno analitico.
- **Delta Lake** en todas las capas: transacciones ACID, MERGE para idempotencia
  e historial de versiones.
- **Lectura cross-workspace** solo en la ingesta (Bronze), que es el unico punto
  que toca el sistema de origen.
