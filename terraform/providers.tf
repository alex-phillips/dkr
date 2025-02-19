terraform {
  required_version = ">= 0.13.0"

  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "2.9.14"
    }

    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.0"
    }

#    oci = {
#      version = "5.22.0"
#    }

    null = {
      source  = "hashicorp/null"
      version = "3.2.3"
    }

    terracurl = {
      source  = "devops-rob/terracurl"
      version = "1.2.2"
    }

    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cfg.cloudflare.api_token
}

provider "proxmox" {
  pm_api_url      = var.cfg.proxmox.api_url
  pm_user         = var.cfg.proxmox.user
  pm_password     = var.cfg.proxmox.password
  pm_tls_insecure = "true"
  pm_timeout      = 3600
  pm_debug        = true
}

provider "oci" {
  tenancy_ocid = var.cfg.oracle.tenancy_ocid
  user_ocid    = var.cfg.oracle.user_ocid
  private_key  = var.cfg.oracle.pem
  fingerprint  = var.cfg.oracle.fingerprint
  region       = var.cfg.oracle.region
}

provider "dns" {
  # Configuration options
}

provider "terracurl" {
  # No configuration required here
}

provider "digitalocean" {
  token = var.cfg.do.token
}
