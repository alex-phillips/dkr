locals {
  cfg = read_terragrunt_config("cfg.hcl")
}

generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket  = "terraform"
    key     = "terraform.tfstate"
    encrypt = true

    endpoint   = "${local.cfg.locals.state.s3_endpoint}"
    access_key = "${local.cfg.locals.state.s3_access_key}"
    secret_key = "${local.cfg.locals.state.s3_secret_key}"

    region                      = "main"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true
  }
}
EOF
}

inputs = {
  cfg = local.cfg.locals
}

terraform {
  source = get_parent_terragrunt_dir()
}
