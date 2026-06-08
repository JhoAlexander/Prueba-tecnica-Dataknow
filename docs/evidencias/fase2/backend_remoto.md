# Evidencia — Backend remoto del estado

El estado de Terraform se almacena en **HCP Terraform** (Terraform Cloud),
no en el repositorio.

## Workspace

| Atributo | Valor |
|---|---|
| Organizacion | retailmax-iac-alexander-dataknow |
| Workspace | retailmax-infra |
| Execution mode | local |
| Terraform version | 1.15.5 |
| Recursos en estado | 4 |

## Modo de ejecucion local

El workspace usa *local execution mode*: HCP Terraform almacena el estado de
forma remota, mientras `plan` y `apply` se ejecutan localmente con la identidad
de Azure CLI (`az login`). Asi no se almacenan credenciales en la nube.

## Verificacion

`terraform state list` (lee desde el backend remoto):

```
fabric_lakehouse.layers["bronze"]
fabric_lakehouse.layers["gold"]
fabric_lakehouse.layers["silver"]
fabric_workspace.this
```

`terraform plan` tras la migracion:

```
No changes. Your infrastructure matches the configuration.
```

## Cumplimiento

- Estado en backend remoto (no en el repositorio).
- `terraform.tfstate` excluido por `.gitignore`.
- Credenciales fuera del codigo (Azure CLI + token de TFC en el perfil local).
