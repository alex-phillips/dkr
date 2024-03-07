resource "oci_core_network_security_group" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
}

resource "oci_core_network_security_group_security_rule" "egress" {
  network_security_group_id = oci_core_network_security_group.this.id
  direction                 = "EGRESS"
  protocol                  = "all"
  description               = "nsg-egress"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
}

resource "oci_core_network_security_group_security_rule" "ingress_ssh" {
  network_security_group_id = oci_core_network_security_group.this.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  description               = "nsg-ingress_ssh"

  source      = "${data.external.public_ip.result.ip}/32"
  source_type = "CIDR_BLOCK"

  destination = oci_core_vcn.this.cidr_blocks[0]

  tcp_options {
    destination_port_range {
      min = 22
      max = 3010
    }
  }
}

resource "oci_core_network_security_group_security_rule" "ingress_all_from_home" {
  network_security_group_id = oci_core_network_security_group.this.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  description               = "nsg-ingress_ssh"

  source      = "${data.external.public_ip.result.ip}/32"
  source_type = "CIDR_BLOCK"

  destination = oci_core_vcn.this.cidr_blocks[0]

  tcp_options {
    destination_port_range {
      min = 1
      max = 65535
    }
  }
}
