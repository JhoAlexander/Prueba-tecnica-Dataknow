# Recursos de Fabric: workspace, lakehouses Medallion y roles.

resource "fabric_workspace" "this" {
  display_name = var.workspace_display_name
  description  = var.workspace_description
  capacity_id  = var.capacity_id
}

# Un lakehouse por capa (bronze, silver, gold).
resource "fabric_lakehouse" "layers" {
  for_each = toset(var.lakehouse_layers)

  display_name = "${var.lakehouse_prefix}_${each.value}"
  workspace_id = fabric_workspace.this.id
  description  = "Capa ${each.value} de la arquitectura Medallion"
}

# Asignaciones de rol parametrizadas (vacio por defecto).
resource "fabric_workspace_role_assignment" "this" {
  for_each = { for ra in var.role_assignments : ra.principal_id => ra }

  workspace_id = fabric_workspace.this.id
  role         = each.value.role

  principal = {
    id   = each.value.principal_id
    type = each.value.principal_type
  }
}
