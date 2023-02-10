resource "oci_core_internet_gateway" "this" {
  compartment_id = var.compartment_id
  display_name   = "igw"
  vcn_id         = oci_core_vcn.this.id
}

resource "oci_core_default_route_table" "this" {
  manage_default_resource_id = oci_core_vcn.this.default_route_table_id
  display_name               = "rt-default"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.this.id
  }
}

resource "oci_core_vcn" "this" {
  #Required
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]

  #Optional
  # byoipv6cidr_details {
  #   #Required
  #   byoipv6range_id = oci_core_byoipv6range.test_byoipv6range.id
  #   ipv6cidr_block  = var.vcn_byoipv6cidr_details_ipv6cidr_block
  # }
  # cidr_block                       = var.vcn_cidr_block
  # cidr_blocks                      = var.vcn_cidr_blocks
  # defined_tags                     = { "Operations.CostCenter" = "42" }
  # display_name                     = var.vcn_display_name
  # dns_label                        = var.vcn_dns_label
  # freeform_tags                    = { "Department" = "Finance" }
  # ipv6private_cidr_blocks          = var.vcn_ipv6private_cidr_blocks
  # is_ipv6enabled                   = var.vcn_is_ipv6enabled
  # is_oracle_gua_allocation_enabled = var.vcn_is_oracle_gua_allocation_enabled
}

resource "oci_core_subnet" "this" {
  #Required
  compartment_id  = var.compartment_id
  vcn_id          = oci_core_vcn.this.id
  cidr_block      = "10.0.0.0/16"
  route_table_id  = oci_core_default_route_table.this.id
  dhcp_options_id = oci_core_vcn.this.default_dhcp_options_id

  security_list_ids = [
    oci_core_security_list.this.id
  ]

  #Optional
  # availability_domain        = var.subnet_availability_domain
  # defined_tags               = { "Operations.CostCenter" = "42" }
  # dhcp_options_id            = oci_core_dhcp_options.test_dhcp_options.id
  # display_name               = var.subnet_display_name
  # dns_label                  = var.subnet_dns_label
  # freeform_tags              = { "Department" = "Finance" }
  # ipv6cidr_block             = var.subnet_ipv6cidr_block
  # ipv6cidr_blocks            = var.subnet_ipv6cidr_blocks
  # prohibit_internet_ingress  = var.subnet_prohibit_internet_ingress
  # prohibit_public_ip_on_vnic = var.subnet_prohibit_public_ip_on_vnic
  # route_table_id             = oci_core_route_table.test_route_table.id
  # security_list_ids          = var.subnet_security_list_ids
}
