variable "compartment_id" {
  type        = string
  description = "Compartment ID to deploy resources"
}

variable "region" {
  type        = string
  description = "Region for deployment"
}

variable "instance_count" {
  type        = number
  default     = 1
  description = "Number of instances to deploy"
}

variable "ssh_keys" {
  type        = string
  description = "SSH Keys to pass to VM instances"
  default     = ""
}

variable "availability_domain_index" {
  type = number
  default = 0
}
