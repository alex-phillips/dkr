terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "2.9.14"
    }

    # cloudflare = {
    #   source  = "cloudflare/cloudflare"
    #   version = "~> 3.0"
    # }

    oci = {
      version = "4.114.0"
    }
  }
}

# provider "cloudflare" {
#   api_token = var.cloudflare_api_token
# }

provider "proxmox" {
  pm_api_url      = var.cfg.proxmox.api_url
  pm_user         = var.cfg.proxmox.user
  pm_password     = var.cfg.proxmox.password
  pm_tls_insecure = "true"
  pm_timeout      = 3600
  pm_debug        = true
}

provider "oci" {
  tenancy_ocid     = var.cfg.oracle.tenancy_ocid
  user_ocid        = var.cfg.oracle.user_ocid
  private_key_path = trimspace(var.cfg.oracle.pem)
  fingerprint      = var.cfg.oracle.fingerprint
  region           = var.cfg.oracle.region
}
