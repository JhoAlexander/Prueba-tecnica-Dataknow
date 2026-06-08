# Salidas con los identificadores de los recursos creados.

output "workspace_id" {
  description = "ID del workspace"
  value       = fabric_workspace.this.id
}

output "workspace_url" {
  description = "URL del workspace en Fabric"
  value       = "https://app.fabric.microsoft.com/groups/${fabric_workspace.this.id}"
}

output "lakehouse_ids" {
  description = "ID de cada lakehouse por capa"
  value       = { for layer, lh in fabric_lakehouse.layers : layer => lh.id }
}

output "environment" {
  description = "Entorno desplegado"
  value       = var.environment
}
