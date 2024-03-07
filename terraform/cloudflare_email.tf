# resource "cloudflare_email_routing_address" "emailalex_net" {
#   account_id = var.cfg.cloudflare.account_id
#   email      = "ahp118@gmail.com"
# }

# resource "cloudflare_email_routing_settings" "emailalex_net" {
#   zone_id = var.cfg.cloudflare.zones["emailalex.net"]
#   enabled = true
# }

resource "cloudflare_email_routing_catch_all" "emailalex_net" {
  zone_id = var.cfg.cloudflare.zones["emailalex.net"]
  name    = "emailalex.net catch-all"
  enabled = true

  matcher {
    type = "all"
  }

  action {
    type  = "forward"
    value = ["ahp118@gmail.com"]
  }
}
