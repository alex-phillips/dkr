# variable "cloudflare_api_token" {
#   type        = string
#   description = "CloudFlare API Token"
# }

variable "cfg" {
  type = any
}

variable "run_ansible" {
  type    = bool
  default = true
}
