#resource "proxmox_vm_qemu" "lsio-jenkins-worker" {
#  count       = 1
#  name        = "charmander"
#  target_node = "mew"
#  clone       = "ubuntu-2004-cloudinit"
#  full_clone  = true
#  cores       = 2
#  sockets     = "1"
#  cpu         = "host"
#  memory      = 2048
#  balloon     = 1024
#  scsihw      = "virtio-scsi-pci"
#  bootdisk    = "scsi0"
#
#  os_type   = "cloud-init"
#  ciuser    = var.ciuser
#  ipconfig0 = "ip=192.168.1.4/24,gw=192.168.1.1"
#  sshkeys   = <<EOF
#${var.ssh_key}
#EOF
#
#  disk {
#    size         = "40G"
#    type         = "scsi"
#    storage      = "local-lvm"
#    iothread     = true
#  }
#
#  network {
#    model  = "virtio"
#    bridge = "vmbr0"
#  }
#
#  lifecycle {
#    ignore_changes = [
#      network,
#    ]
#  }
#}
