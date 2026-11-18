terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

#var.name format
provider "aws" {
  region = var.region
  #read variable tag above. configure aws plug in
  default_tags {
    tags = {
      Project   = "djangoapp"
      ManagedBy = "terraform"
    }
  }
}

#pull out data , current is nickname for tfstate
data "aws_caller_identity" "current" {}

#tfstate is nickname for tfstate usage.This is building bicket
resource "aws_s3_bucket" "tfstate" {
  bucket = "djangoapp-tfstate-${data.aws_caller_identity.current.account_id}"

}

#change setting on that bucket 
resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id

  versioning_configuration {
    status = "Enabled"
  }
}


output "state_bucket" {
  value = aws_s3_bucket.tfstate.bucket
}