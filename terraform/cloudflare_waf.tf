resource "cloudflare_filter" "wordpress" {
  for_each    = var.cfg.cloudflare.zones
  zone_id     = each.value
  description = "Wordpress break-in attempts that are outside of the office"
  expression  = "(http.request.uri.path contains \"wp-login.php\" and http.request.uri.path contains \"xmlrpc.php\") and not ip.src in {${data.external.public_ip.result.ip}}"
}

resource "cloudflare_filter" "us_only" {
  for_each    = var.cfg.cloudflare.zones
  zone_id     = each.value
  description = "Requests not from the US"
  expression  = "(not ip.geoip.country in {\"CA\" \"US\" \"GB\"})"
}

resource "cloudflare_firewall_rule" "wordpress" {
  for_each    = var.cfg.cloudflare.zones
  zone_id     = each.value
  description = "Block wordpress break-in attempts"
  filter_id   = cloudflare_filter.wordpress[each.key].id
  action      = "block"
}

resource "cloudflare_firewall_rule" "us_only" {
  for_each    = var.cfg.cloudflare.zones
  zone_id     = each.value
  description = "Block requests not in the US"
  filter_id   = cloudflare_filter.us_only[each.key].id
  action      = "block"
}
