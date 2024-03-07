output "public_ip" {
  value = oci_core_instance.instance.*.public_ip
}

output "availability_domains" {
  value = data.oci_identity_availability_domains.this.availability_domains
}
