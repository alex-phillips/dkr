# variable "cloudflare_api_token" {
#   type        = string
#   description = "CloudFlare API Token"
# }

variable "proxmox_host" {
  default = "192.168.1.151:8006"
}

variable "proxmox_password" {
  default = "root"
}

variable "ssh_key" {
  default = ""
}

variable "ciuser" {
  default = "ubuntu"
}

variable "lxc_password" {
  default = ""
}

variable "cfg" {
  type = any
}
