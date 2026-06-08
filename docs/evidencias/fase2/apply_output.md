# Evidencia — terraform apply (entorno dev)

Salida del despliegue exitoso.

```
fabric_workspace.this: Creating...
fabric_workspace.this: Creation complete after 20s [id=60259c60-ec61-406c-94c9-305e41badf4c]
fabric_lakehouse.layers["bronze"]: Creating...
fabric_lakehouse.layers["silver"]: Creating...
fabric_lakehouse.layers["gold"]: Creating...
fabric_lakehouse.layers["silver"]: Creation complete after 38s [id=cca20c1b-8219-4641-88e0-16fc9cf3be56]
fabric_lakehouse.layers["gold"]: Creation complete after 38s [id=07875980-48ed-4203-95cc-c992a1e7e37a]
fabric_lakehouse.layers["bronze"]: Creation complete after 38s [id=5d469c7d-d1b6-4166-89df-3caa8b8e6dc1]

Apply complete! Resources: 4 added, 0 changed, 0 destroyed.

Outputs:

environment = "dev"
lakehouse_ids = {
  "bronze" = "5d469c7d-d1b6-4166-89df-3caa8b8e6dc1"
  "gold" = "07875980-48ed-4203-95cc-c992a1e7e37a"
  "silver" = "cca20c1b-8219-4641-88e0-16fc9cf3be56"
}
workspace_id = "60259c60-ec61-406c-94c9-305e41badf4c"
workspace_url = "https://app.fabric.microsoft.com/groups/60259c60-ec61-406c-94c9-305e41badf4c"
```
