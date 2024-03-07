# resource "local_file" "ansible_hosts" {
#   filename = "${path.module}/ansible/hosts"
#   content = yamlencode({
#     all = {
#       children = {
#         oracle = {
#           hosts = {
#             for ip in module.oracle.public_ip : ip => {
#               ansible_user                         = "ubuntu"
#               docker_apt_arch                      = "arm64"
#               docker_compose_arch                  = "aarch64"
#               docker_compose_generator_output_path = "/home/{{ ansible_user }}"
#             }
#           }
#         }
#       }
#     }
#   })
# }

# resource "null_resource" "ansible_oracle" {
#   count = var.run_ansible == true ? 1 : 0

#   triggers = {
#     # ips = join(",", module.oracle.public_ip)
#     time = timestamp()
#   }

#   provisioner "local-exec" {
#     command = "ansible-galaxy install -r ansible/galaxy-requirements.yml && ansible-playbook -i ansible/hosts ansible/main.yml"
#   }
# }
