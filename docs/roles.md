# Roles, accesos y auditoria

## Los tres roles

| Rol | Acceso a los datos | Implementacion en Fabric |
|---|---|---|
| **Administrador** | Control total sobre el workspace y los recursos | Rol **Admin** del workspace |
| **Ingeniero de Datos** | Lectura y escritura en todas las capas (Bronze, Silver, Gold) | Rol **Member** del workspace dev |
| **Analista** | Solo lectura de la capa Gold | Acceso compartido **solo al lakehouse `lh_gold`** (lectura); no es miembro del workspace |

## Principio de minimo privilegio

Cada rol recibe **solo** los permisos que necesita:
- El Analista no es miembro del workspace, por lo que **no puede ver Bronze ni
  Silver**. Solo accede al lakehouse Gold que se le compartio explicitamente.
- El Ingeniero opera las tres capas, pero no administra el workspace ni los
  permisos de otros usuarios.
- El Administrador gestiona recursos y accesos, pero el procesamiento corre bajo
  las identidades de servicio del pipeline, no bajo su cuenta personal.

## Identidades de servicio del pipeline

El pipeline se autentica con la identidad del propietario del notebook/pipeline
en Fabric. Ninguna credencial aparece en el codigo: la conexion a OneLake usa la
identidad de la sesion, y los secretos de infraestructura se gestionan fuera del
repositorio (ver Fase 2).

## Mecanismo de acceso por capa (minimo privilegio)

El control de acceso del Analista se implementa con el modelo de permisos a
nivel de item de Fabric:

1. El Analista **no se agrega como miembro del workspace** (si lo fuera, veria
   todos los lakehouses, incluidos Bronze y Silver).
2. Se le **comparte unicamente `lh_gold`** con permiso de **lectura** (opcion
   "Manage permissions" / "Share" del lakehouse).
3. Como Bronze y Silver no se comparten, **no aparecen** para el Analista y la
   navegacion directa a ellos devuelve "sin acceso".

La evidencia es la pantalla de **permisos compartidos de `lh_gold`** en
`docs/evidencias/fase5/`, que muestra el modelo de acceso de solo lectura
limitado a la capa Gold.

> Nota de entorno: el tenant de evaluacion (creado para la prueba) no permite
> crear usuarios internos adicionales con la cuenta disponible (sin rol de
> Administrador global). Por eso la evidencia documenta el **mecanismo de
> permisos por item** en lugar de un segundo inicio de sesion. En un tenant con
> licencias completas, el Analista iniciaria sesion y veria unicamente Gold.

## Auditoria de accesos

Microsoft Fabric registra de forma nativa los accesos a los datos:
- El **registro de auditoria de Microsoft 365 / Purview** captura eventos de
  acceso, lectura y exportacion por usuario y marca de tiempo.
- El **Monitor Hub** de Fabric registra cada ejecucion de notebook y pipeline.
- Estos registros permiten responder "quien accedio a que dato y cuando" sin
  instrumentacion adicional.

## Gestion de roles como codigo

El recurso `fabric_workspace_role_assignment` del codigo Terraform (carpeta
`infra/`) permite asignar los roles de workspace de forma declarativa y
versionada, en lugar de hacerlo manualmente en la interfaz.
