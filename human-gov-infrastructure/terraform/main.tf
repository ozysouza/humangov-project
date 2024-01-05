provider "aws" {
  region = "us-east-1"
}

module "aws_humangov_infrastructure" {
  source     = "./modules/aws_humangov_infrastructure"
  for_each   = toset(var.states)
  state_name = each.value
}