locals {
  # env = { for tuple in regexall("(.*)=(.*)", file("./.env")) : tuple[0] => tuple[1] }
}
