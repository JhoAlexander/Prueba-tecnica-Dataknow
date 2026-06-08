# Provider de Microsoft Fabric y configuracion de Terraform.

terraform {
  required_version = ">= 1.8"

  required_providers {
    fabric = {
      source  = "microsoft/fabric"
      version = "~> 1.0"
    }
  }

  # Backend remoto en HCP Terraform (state remoto, ejecucion local).
  cloud {
    organization = "retailmax-iac-alexander-dataknow"
    workspaces {
      name = "retailmax-infra"
    }
  }
}

# Autenticacion via Azure CLI (az login). Sin credenciales en codigo.
provider "fabric" {
  tenant_id = var.tenant_id
}
