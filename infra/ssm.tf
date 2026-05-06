# Store secrets in AWS SSM Parameter Store (encrypted)
# ECS task pulls these at runtime — never stored in the image

resource "aws_ssm_parameter" "adzuna_app_id" {
  name  = "/${var.app_name}/${var.env}/adzuna_app_id"
  type  = "SecureString"
  value = var.adzuna_app_id
}

resource "aws_ssm_parameter" "adzuna_app_key" {
  name  = "/${var.app_name}/${var.env}/adzuna_app_key"
  type  = "SecureString"
  value = var.adzuna_app_key
}

resource "aws_ssm_parameter" "anthropic_api_key" {
  name  = "/${var.app_name}/${var.env}/anthropic_api_key"
  type  = "SecureString"
  value = var.anthropic_api_key
}
