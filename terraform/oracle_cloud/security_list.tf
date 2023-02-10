# create empty security list to avoid using 'default' with open 22
resource "oci_core_security_list" "this" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.this.id
  display_name   = "seclist"
}
