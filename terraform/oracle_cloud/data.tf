data "oci_core_images" "os" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}


data "external" "public_ip" {
  program = [
    "sh",
    "-c",
    "curl -s ifconfig.co | xargs -I {} echo '{\"ip\":\"{}\"}'",
  ]
  # program = [
  #   "curl",
  #   "https://api.ipify.org?format=json",
  # ]
}
