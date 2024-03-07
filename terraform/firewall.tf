# resource "terracurl_request" "test" {
#   name   = "firewall-rule-test"
#   url    = "https://192.168.1.1/api/firewall/rules"
#   method = "POST"
#   request_body = jsonencode({
#     action      = "Pass"
#     interface   = "WAN"
#     protocol    = "TCP/UDP"
#     source      = "*"
#     destination = "192.168.1.91:8843"
#   })

#   headers = {
#     Authorization = "ApiKey s9MBdYefGfFXCdRhpu+KxFoWWpBkhub+aN4//NpWinY6UICs7/d+gL6oecuDhBQatUEZh/6KO5g+PXp0:IebqAfvrJsCBi4lcxR2rvBmgJDQ87U2qwEoNgxkBzcFbhsgHGrN1c/EcNJH4+23WY1WWopdBOX87UmXU"
#   }

#   response_codes = [
#     200,
#     204,
#   ]

#   # cert_file       = "server-vault-0.pem"
#   # key_file        = "server-vault-0-key.pem"
#   # ca_cert_file    = "vault-server-ca.pem"
#   # skip_tls_verify = false


#   # destroy_url    = "https://localhost:8200/v1/sys/mounts/aws"
#   # destroy_method = "DELETE"

#   # destroy_headers = {
#   #   X-Vault-Token = "root"
#   # }

#   # destroy_response_codes = [
#   #   204
#   # ]

#   # destroy_cert_file       = "server-vault-0.pem"
#   # destroy_key_file        = "server-vault-0-key.pem"
#   # destroy_ca_cert_file    = "vault-server-ca.pem"
#   # destroy_skip_tls_verify = false
# }

# output "response" {
#   value = terracurl_request.test.response
# }
