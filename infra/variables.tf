variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"   # Ireland
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "irish-jobs"
}

variable "env" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "db_password" {
  description = "RDS PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "adzuna_app_id" {
  description = "Adzuna API app ID"
  type        = string
  sensitive   = true
}

variable "adzuna_app_key" {
  description = "Adzuna API app key"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic Claude API key"
  type        = string
  sensitive   = true
}
