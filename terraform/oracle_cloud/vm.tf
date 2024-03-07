locals {
  user_data = <<EOF
#!/bin/bash

sudo apt update
sudo apt upgrade -y
EOF
}

data "oci_identity_availability_domains" "this" {
  compartment_id = var.compartment_id
}

resource "oci_core_instance" "instance" {
  count = var.instance_count

  availability_domain = data.oci_identity_availability_domains.this.availability_domains[1].name
  compartment_id      = var.compartment_id
  display_name        = "instance-${count.index}"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4 / var.instance_count
    memory_in_gbs = 24 / var.instance_count
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.this.id
    assign_public_ip = true
    nsg_ids          = [oci_core_network_security_group.this.id]
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.os.images[0].id
    boot_volume_size_in_gbs = 200 / var.instance_count
  }

  metadata = {
    ssh_authorized_keys = var.ssh_keys
    user_data           = base64encode(local.user_data)
  }


  lifecycle {
    ignore_changes = [
      # Ignore changes to source_details, so that instance isn't
      # recreated when a new image releases. Also allows for easy
      # resource import.
      source_details[0].source_id,
    ]
  }
}

data "oci_core_vnic_attachments" "a1_vnic_attachments" {
  count = var.instance_count

  compartment_id = var.compartment_id
  instance_id    = oci_core_instance.instance[count.index].id
}
