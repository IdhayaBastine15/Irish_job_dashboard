terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Store Terraform state in S3 — create this bucket manually first
  # aws s3 mb s3://irish-jobs-tf-state --region eu-west-1
  backend "s3" {
    bucket = "irish-jobs-tf-state"
    key    = "prod/terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = var.aws_region
}
