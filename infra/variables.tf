# Variables de entrada parametrizadas.

variable "tenant_id" {
  description = "ID del tenant de Entra ID"
  type        = string
}

variable "capacity_id" {
  description = "ID de la capacidad de Fabric a asignar al workspace"
  type        = string
}

variable "environment" {
  description = "Nombre del entorno (dev / prod)"
  type        = string
}

variable "workspace_display_name" {
  description = "Nombre visible del workspace"
  type        = string
}

variable "workspace_description" {
  description = "Descripcion del workspace"
  type        = string
  default     = ""
}

variable "lakehouse_layers" {
  description = "Capas Medallion a crear como lakehouses"
  type        = list(string)
  default     = ["bronze", "silver", "gold"]
}

variable "lakehouse_prefix" {
  description = "Prefijo para el nombre de cada lakehouse"
  type        = string
  default     = "lh"
}

variable "role_assignments" {
  description = "Asignaciones de rol en el workspace"
  type = list(object({
    principal_id   = string
    principal_type = string
    role           = string
  }))
  default = []
}
