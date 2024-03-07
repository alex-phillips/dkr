data "http" "public_keys" {
  url = "https://github.com/alex-phillips.keys"
}

#module "oracle" {
#  source                    = "./oracle_cloud"
#  region                    = "us-ashburn-1"
#  compartment_id            = "ocid1.tenancy.oc1..aaaaaaaafy3hea5pvopvntwbzcx4hjms2vtzgaxlq6i4acxinv3la6rdmw3q"
#  ssh_keys                  = data.http.public_keys.response_body
#  instance_count            = 1
#  availability_domain_index = 1
#}

# oci1151
# 3hFVDEvUpq6xWnU$pJdXxU*b!hJF9E7Le3jySNy
