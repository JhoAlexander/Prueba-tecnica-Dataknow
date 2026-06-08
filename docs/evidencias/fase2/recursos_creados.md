# Recursos creados — Infraestructura

Recursos aprovisionados por Terraform en el entorno **dev**.

## Workspace

| Atributo | Valor |
|---|---|
| Tipo | `fabric_workspace` |
| Nombre | RetailMax-Lab-DataKnow-dev |
| ID | `60259c60-ec61-406c-94c9-305e41badf4c` |
| Capacidad | FTL64 (trial) |
| Region | West US |
| URL | https://app.fabric.microsoft.com/groups/60259c60-ec61-406c-94c9-305e41badf4c |

## Lakehouses (arquitectura Medallion)

| Capa | Nombre | ID | Proposito |
|---|---|---|---|
| Bronze | lh_bronze | `5d469c7d-d1b6-4166-89df-3caa8b8e6dc1` | Ingesta cruda desde la fuente |
| Silver | lh_silver | `cca20c1b-8219-4641-88e0-16fc9cf3be56` | Limpieza, tipado y conformidad |
| Gold | lh_gold | `07875980-48ed-4203-95cc-c992a1e7e37a` | Modelo dimensional y agregados |

Cada lakehouse incluye automaticamente un SQL Analytics Endpoint.

## Verificacion independiente

Listado de items via API de Fabric (independiente del estado de Terraform):

```
Nombre     Tipo
---------  -----------
lh_bronze  Lakehouse
lh_silver  Lakehouse
lh_gold    Lakehouse
lh_bronze  SQLEndpoint
lh_silver  SQLEndpoint
lh_gold    SQLEndpoint
```
