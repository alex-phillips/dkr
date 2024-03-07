locals {
  w00t_cloud_cnames = {
    "w00t.cloud" = {
      value   = "wootables.duckdns.org"
      proxied = true
    }
    "*" = {
      proxied = true
    }
    # "hls-proxy" = {}
    "mb" = {
      # proxied = true
    }
    "mqtt" = {}
    "nc"   = {}
    # "nm-broker" = {}
    "sync"     = {}
    "tv-proxy" = {}
    "tv"       = {}
  }
}

# resource "cloudflare_record" "origin_w00t_cloud" {
#   zone_id = var.cfg.cloudflare.zones["w00t.cloud"]
#   name    = "origin"
#   value   = "64.99.193.234"
#   type    = "A"
#   proxied = false

#   lifecycle {
#     ignore_changes = [
#       value
#     ]
#   }
# }

resource "cloudflare_record" "w00t_cloud_cnames" {
  for_each = local.w00t_cloud_cnames
  zone_id  = var.cfg.cloudflare.zones["w00t.cloud"]
  name     = each.key
  value    = try(each.value.value, "w00t.cloud")
  type     = "CNAME"
  proxied  = try(each.value.proxied, false)
}
