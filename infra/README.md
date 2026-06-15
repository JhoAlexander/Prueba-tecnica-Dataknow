# infra

Infraestructura como Codigo (Terraform) para Microsoft Fabric.

Despliega un workspace con su arquitectura Medallion (lakehouses bronze,
silver y gold) de forma reproducible y parametrizada por entorno.

## Requisitos

- Terraform >= 1.8
- Azure CLI (`az`)
- Sesion iniciada: `az login --allow-no-subscriptions`
- Capacidad de Fabric (trial)

## Archivos

```
providers.tf              Provider de Fabric y backend
variables.tf              Variables de entrada
main.tf                   Workspace, lakehouses y roles
outputs.tf                Identificadores de salida
environments/
  dev.tfvars              Valores del entorno dev
  prod.tfvars             Valores del entorno prod
terraform.tfvars.example  Plantilla de IDs (copiar a terraform.tfvars)
```

`terraform.tfvars` (con `tenant_id` y `capacity_id`) no se versiona.

## Despliegue

```powershell
# 1. Preparar variables locales
Copy-Item terraform.tfvars.example terraform.tfvars
#   editar terraform.tfvars con tenant_id y capacity_id reales

# 2. Inicializar
terraform init

# 3. Revisar el plan del entorno dev
terraform plan -var-file="environments/dev.tfvars"

# 4. Aplicar
terraform apply -var-file="environments/dev.tfvars"

# 5. Ver salidas
terraform output
```

Para destruir el entorno: `terraform destroy -var-file="environments/dev.tfvars"`.

## Entornos

| Entorno | Workspace | Gestion |
|---|---|---|
| dev | `RetailMax-Lab-DataKnow-dev` | Terraform |
| prod | `RetailMax-Lab-DataKnow` | Existente (UI); `prod.tfvars` documenta la parametrizacion equivalente |

El mismo codigo despliega cualquier entorno cambiando el `-var-file`.

## Recursos creados (entorno dev)

| Recurso | Nombre | Region | Proposito |
|---|---|---|---|
| `fabric_workspace` | RetailMax-Lab-DataKnow-dev | West US | Workspace del entorno dev |
| `fabric_lakehouse` | lh_bronze | West US | Capa Bronze (ingesta cruda) |
| `fabric_lakehouse` | lh_silver | West US | Capa Silver (limpieza y conformidad) |
| `fabric_lakehouse` | lh_gold | West US | Capa Gold (modelo analitico) |

## Seguridad

- Autenticacion via Azure CLI; sin credenciales en el codigo.
- `tenant_id` y `capacity_id` en `terraform.tfvars` (no versionado).
- El estado se almacena en backend remoto; nunca se confirma en el repositorio.
