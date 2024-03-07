# resource "proxmox_lxc" "shelder" {
#   hostname = "shelder"
#   # cores    = 8
#   # memory   = "9999"
#   # swap     = "1024"

#   network {
#     name     = "eth0"
#     bridge   = "vmbr0"
#     ip       = "192.168.1.90/24"
#     firewall = false
#   }

#   ostemplate = "local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz"
#   password   = var.lxc_password
#   pool       = ""
#   # rootfs       = "local-lvm:8"
#   # storage      = "local-lvm"
#   target_node  = "mew"
#   unprivileged = true
#   start        = true

#   rootfs {
#     storage = "local-lvm"
#     size    = "8G"
#   }

#   # features {
#   #   keyctl  = true
#   #   nesting = true
#   # }
# }
