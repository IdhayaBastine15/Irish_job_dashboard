output "alb_dns_name" {
  description = "Public URL of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for docker push"
  value       = aws_ecr_repository.backend.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = aws_opensearch_domain.main.endpoint
}

output "s3_bucket_name" {
  description = "S3 bucket for resume uploads"
  value       = aws_s3_bucket.resumes.bucket
}

output "github_actions_role_arn" {
  description = "IAM role ARN to add as GitHub secret AWS_ROLE_ARN"
  value       = aws_iam_role.github_actions.arn
}
