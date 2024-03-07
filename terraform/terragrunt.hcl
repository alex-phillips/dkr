locals {
  cfg = try(read_terragrunt_config("cfg.hcl"), {})

  state = {
    s3_endpoint   = try(local.cfg.locals.state.s3_endpoint, get_env("TF_VAR_state_s3_endpoint"))
    s3_access_key = try(local.cfg.locals.state.s3_access_key, get_env("TF_VAR_state_s3_access_key"))
    s3_secret_key = try(local.cfg.locals.state.s3_secret_key, get_env("TF_VAR_state_s3_secret_key"))
  }

  cloudflare = {
    api_token  = try(local.cfg.locals.cloudflare.api_token, get_env("TF_VAR_cloudflare_api_token"))
    account_id = "d8c3edf755048d324817ee5c4eaf3936"
    zones = {
      "w00t.cloud"       = "9601db709d5afaf69d1a2fe3c8150237"
      "wootables.com"    = "26115d7fa75a7e21a73e2b4c70c94e4d"
      "emailalex.net"    = "d8167f22e8f6a398b08c5b46035f448a"
      "emailspencer.net" = "ea100c16d2e43bbe8992a77f929974c0"
    }
  }

  #####
  # Proxmox
  #####
  proxmox = {
    user     = try(local.cfg.locals.proxmox.user, get_env("TF_VAR_proxmox_user"))
    password = try(local.cfg.locals.proxmox.password, get_env("TF_VAR_proxmox_password"))
    api_url  = try(local.cfg.locals.proxmox.api_url, get_env("TF_VAR_proxmox_api_url"))
  }

  #####
  # Oracle Cloud
  #####
  oracle = {
    tenancy_ocid = try(local.cfg.locals.oracle.tenancy_ocid, get_env("TF_VAR_oracle_tenancy_ocid"))
    user_ocid    = try(local.cfg.locals.oracle.user_ocid, get_env("TF_VAR_oracle_user_ocid"))
    fingerprint  = try(local.cfg.locals.oracle.fingerprint, get_env("TF_VAR_oracle_fingerprint"))
    region       = try(local.cfg.locals.oracle.region, get_env("TF_VAR_oracle_region"))
    pem          = try(local.cfg.locals.oracle.pem, get_env("TF_VAR_oracle_pem"))
  }

  opnsense = {
    api_key = try(local.cfg.locals.opnsense.api_key, get_env("TF_VAR_opnsense_api_key"))
  }
}

generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket  = "terraform"
    key     = "terraform.tfstate"

    endpoint   = "${local.state.s3_endpoint}"
    access_key = "${local.state.s3_access_key}"
    secret_key = "${local.state.s3_secret_key}"

    region                      = "main"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true
    skip_requesting_account_id  = true
  }
}
EOF
}

inputs = {
  cfg = {
    cloudflare = local.cloudflare
    proxmox    = local.proxmox
    oracle     = local.oracle
    opnsense   = local.opnsense
  }
}

terraform {
  source = "${get_parent_terragrunt_dir()}///" # this is dumb, but this prevents the stupid terragrunt warning about double slashes?
}
