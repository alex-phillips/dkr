resource "digitalocean_droplet" "this" {
  image  = "ubuntu-20-04-x64"
  name   = var.name
  region = "nyc2"
  size   = "s-1vcpu-1gb"
}
