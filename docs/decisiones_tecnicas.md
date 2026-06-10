# Decisiones tecnicas

Registro de las decisiones de diseno principales, con su justificacion y
alternativas consideradas.

## 1. Plataforma: Microsoft Fabric

**Decision:** Microsoft Fabric (capacidad trial F64).
**Alternativas:** Azure con servicios separados (ADLS + ADF + Databricks), AWS, GCP.
**Razon:** Fabric integra storage, procesamiento PySpark, orquestacion y BI en un
unico workspace con OneLake como lake unificado, sin costo durante el trial. Reduce
la complejidad operativa frente a orquestar 5+ servicios separados.
**Consecuencia:** algunas capacidades (backoff exponencial, conectores de correo)
tienen limitaciones que se documentan; a cambio, menor friccion de integracion.

## 2. Formato de tabla: Delta Lake

**Decision:** Delta Lake en todas las capas.
**Alternativas:** Parquet plano.
**Razon:** transacciones ACID, operacion MERGE (clave para la idempotencia),
evolucion de esquema e historial de versiones (time travel).
**Consecuencia:** ligeramente mas metadata por tabla, compensado por la robustez.

## 3. Generacion de datos: Python + Faker

**Decision:** Python con Faker, Pandas y NumPy, semilla fija.
**Alternativas:** generadores SQL, Scala/Spark.
**Razon:** reproducibilidad bit a bit con semilla, distribuciones realistas
(estacionalidad, picos horarios, lognormal) y velocidad (1.86M filas en ~17 s).
**Consecuencia:** la generacion corre en local; los datos se suben al lakehouse.

## 4. IaC: Terraform con provider de Fabric

**Decision:** Terraform (`microsoft/fabric`).
**Alternativas:** Bicep, ARM, configuracion manual por UI.
**Razon:** el provider de Fabric es GA y soporta workspace, lakehouses y roles;
Terraform es multiplataforma y declarativo.
**Consecuencia:** la autenticacion usa Azure CLI; el estado va a un backend remoto.

## 5. Estado remoto: HCP Terraform

**Decision:** HCP Terraform (Terraform Cloud) free tier, ejecucion local.
**Alternativas:** Azure Storage (azurerm backend), estado local.
**Razon:** backend remoto sin costo y sin requerir una suscripcion Azure activa.
El modo de ejecucion local mantiene las credenciales en la maquina (Azure CLI),
no en la nube.
**Consecuencia:** el estado nunca se versiona en el repositorio.

## 6. Dos workspaces (prod / dev)

**Decision:** fuente en workspace prod; Medallion en workspace dev (provisionado
por Terraform).
**Alternativas:** todo en un unico workspace.
**Razon:** separa el origen operacional del entorno analitico y materializa los
dos entornos (dev/prod) que exige la infraestructura. Conecta IaC con el pipeline.
**Consecuencia:** Bronze lee la fuente cross-workspace (unico punto de contacto
con el origen); Silver y Gold fluyen dentro de dev.

## 7. Idempotencia: MERGE y overwrite

**Decision:** Bronze usa MERGE por llave primaria; Silver y Gold sobrescriben.
**Razon:** reejecutar el pipeline no duplica datos ni altera el resultado final.
**Consecuencia:** Bronze conserva el estado actual por llave; el historico de
ingestas queda en la tabla de control `_log_ingesta`.

## 8. Orquestacion: Fabric Data Pipelines

**Decision:** Data Pipeline nativo de Fabric.
**Alternativas:** Apache Airflow, Databricks Workflows.
**Razon:** integrado con el workspace, sin servidor adicional, con scheduling,
reintentos y notificaciones.
**Limitacion documentada:** los reintentos usan intervalo fijo, no backoff
exponencial (no soportado nativamente); las dependencias multiples son AND, lo que
motiva el patron de una alerta por actividad.

## 9. Enmascaramiento de PII: hash SHA-256

**Decision:** `razon_social` se almacena como hash desde Silver.
**Razon:** el dato sensible deja de ser legible aguas abajo pero sigue siendo util
para agrupar (el mismo valor produce el mismo hash). El escenario no contiene
nombres de persona, documentos ni contacto; de existir, se aplicaria igual.

## 10. Notificaciones por correo

**Decision:** actividad Office 365 Outlook para alertas de exito y fallo.
**Hallazgo:** el conector requiere un buzon de Exchange; la identidad del tenant
de Fabric no lo tiene y las cuentas personales no son aceptadas. Se resolvio con
una cuenta de correo con buzon valido. Identidad y buzon son cosas distintas.
