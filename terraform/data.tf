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
