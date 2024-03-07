# variable "k3s_master_nodes" {
#   default = [
#     # {
#     #   "name" : "magikarp",
#     #   "ip" : "192.168.1.129",
#     #   "id" : 200,
#     #   "storage": "evo850-500gb-1",
#     # },
#     # {
#     #   "name" : "gyarados",
#     #   "ip" : "192.168.1.130",
#     #   "id" : 201,
#     #   "storage": "evo850-500gb-1",
#     # },
#     # {
#     #   "name" : "lapras",
#     #   "ip" : "192.168.1.131",
#     #   "id" : 202,
#     #   "storage": "evo850-500gb-1",
#     # },
#   ]
# }

# variable "k3s_worker_nodes" {
#   default = [
#     # {
#     #   "name" : "vaporeon",
#     #   "ip" : "192.168.1.134",
#     #   "id" : 203,
#     #   "storage": "evo850-500gb-2",
#     # },
#     # {
#     #   "name" : "jolteon",
#     #   "ip" : "192.168.1.135",
#     #   "id" : 204,
#     #   "storage": "evo850-500gb-2",
#     # },
#     # {
#     #   "name" : "flareon",
#     #   "ip" : "192.168.1.136",
#     #   "id" : 205,
#     #   "storage": "evo850-500gb-1",
#     # },
#   ]
# }

# // This machine is purely for spinning up and messing with,
# // not meant to be persistent.'
# resource "proxmox_vm_qemu" "k3s-master-node" {
#   for_each = { for vm in var.k3s_master_nodes : vm.name => vm }

#   name        = each.value.name
#   vmid        = each.value.id
#   target_node = "mew"
#   clone       = "ubuntu-2004-cloudinit"
#   full_clone  = true
#   cores       = 2
#   sockets     = "1"
#   cpu         = "host"
#   memory      = 4096
#   scsihw      = "virtio-scsi-pci"
#   bootdisk    = "scsi0"

#   os_type   = "cloud-init"
#   ciuser    = var.ciuser
#   ipconfig0 = "ip=${each.value.ip}/24,gw=192.168.1.1"
#   sshkeys   = <<EOF
# ${var.ssh_key}
# EOF

#   disk {
#     size     = "10G"
#     type     = "scsi"
#     storage  = each.value.storage
#     iothread = 0
#   }

#   network {
#     model  = "virtio"
#     bridge = "vmbr0"
#   }

#   lifecycle {
#     ignore_changes = [
#       network,
#     ]
#   }
# }

# resource "proxmox_vm_qemu" "k3s-worker-node" {
#   for_each = { for vm in var.k3s_worker_nodes : vm.name => vm }

#   name        = each.value.name
#   vmid        = each.value.id
#   target_node = "mew"
#   clone       = "ubuntu-2004-cloudinit"
#   full_clone  = true
#   cores       = 2
#   sockets     = "4"
#   cpu         = "host"
#   memory      = 20480
#   scsihw      = "virtio-scsi-pci"
#   bootdisk    = "scsi0"

#   os_type   = "cloud-init"
#   ciuser    = var.ciuser
#   ipconfig0 = "ip=${each.value.ip}/24,gw=192.168.1.1"
#   sshkeys   = <<EOF
# ${var.ssh_key}
# EOF

#   disk {
#     size    = "200G"
#     type    = "scsi"
#     storage = each.value.storage
#     #iothread = true
#   }

#   network {
#     model  = "virtio"
#     bridge = "vmbr0"
#   }

#   lifecycle {
#     ignore_changes = [
#       network,
#     ]
#   }
# }
