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

resource "oci_core_network_security_group_security_rule" "ingress" {
  network_security_group_id = oci_core_network_security_group.this.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  description               = "nsg-ingress-ssh"

  source      = "${data.external.public_ip.result.ip}/32"
  source_type = "CIDR_BLOCK"

  # destination      = "${oci_core_instance.instance.public_ip}/32"
  destination      = oci_core_vcn.this.cidr_blocks[0]
  destination_type = "CIDR_BLOCK"

  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}
