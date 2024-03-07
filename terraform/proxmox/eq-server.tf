resource "proxmox_vm_qemu" "eq_server" {
  name        = "squirtle"
  target_node = "mew"
  clone       = "ubuntu-2204-cloudinit"
  full_clone  = true
  cores       = 1
  vcpus       = 0
  sockets     = 2
  cpu         = "host"
  memory      = 4096
  scsihw      = "virtio-scsi-pci"
  bootdisk    = "scsi0"

  os_type   = "cloud-init"
  ciuser    = var.ciuser
  ipconfig0 = "ip=192.168.1.7/24,gw=192.168.1.1"
  sshkeys   = <<EOF
${var.ssh_key}
EOF

  disk {
    size     = "20G"
    type     = "scsi"
    storage  = "hdd-lvm"
    iothread = 0
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
}
