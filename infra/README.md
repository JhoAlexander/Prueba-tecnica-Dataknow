# infra

Configuracion de la infraestructura en Microsoft Fabric.

## Recursos

- Workspace de Fabric
- Lakehouse fuente (endpoint SQL como origen del pipeline)
- Lakehouse Medallion con zonas `bronze`, `silver`, `gold` en OneLake
- Data Factory (pipelines de orquestacion)
- Roles y permisos (Ingeniero, Analista, Administrador)
- Alertas por correo

## Enfoque

La configuracion combina aprovisionamiento declarativo (donde el proveedor de
Fabric lo soporta) con pasos de UI documentados con capturas. Los parametros de
nombres y region se mantienen en `parameters.yaml`. Los secretos se gestionan
fuera del codigo.

## Estructura prevista

```
README.md
parameters.yaml      Parametros por entorno (dev / prod)
fabric-setup/        Pasos de configuracion documentados
evidencias/          Capturas del despliegue
```
