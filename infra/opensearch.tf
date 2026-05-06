resource "aws_opensearch_domain" "main" {
  domain_name    = "${var.app_name}-search"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type  = "t3.small.search"   # smallest billable instance
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp2"
  }

  vpc_options {
    subnet_ids         = [aws_subnet.private[0].id]
    security_group_ids = [aws_security_group.opensearch.id]
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = aws_iam_role.ecs_task.arn }
      Action    = "es:*"
      Resource  = "arn:aws:es:${var.aws_region}:*:domain/${var.app_name}-search/*"
    }]
  })

  tags = { Name = "${var.app_name}-opensearch" }
}
