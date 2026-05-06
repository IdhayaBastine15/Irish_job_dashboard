resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.app_name}-backend"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.app_name}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "backend"
    image = "${aws_ecr_repository.backend.repository_url}:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "ADZUNA_BASE_URL",           value = "https://api.adzuna.com/v1/api/jobs/gb" },
      { name = "ADZUNA_RESULTS_PER_PAGE",   value = "50" },
      { name = "ADZUNA_MAX_PAGES",          value = "5" },
      { name = "SYNC_INTERVAL_HOURS",       value = "6" },
      { name = "ELASTICSEARCH_URL",         value = "https://${aws_opensearch_domain.main.endpoint}" },
      { name = "DATABASE_URL",              value = "postgresql+asyncpg://postgres:${var.db_password}@${aws_db_instance.postgres.address}:5432/irish_jobs" },
      { name = "SYNC_DATABASE_URL",         value = "postgresql://postgres:${var.db_password}@${aws_db_instance.postgres.address}:5432/irish_jobs" },
      { name = "S3_BUCKET",                 value = aws_s3_bucket.resumes.bucket },
    ]
    secrets = [
      { name = "ADZUNA_APP_ID",     valueFrom = aws_ssm_parameter.adzuna_app_id.arn },
      { name = "ADZUNA_APP_KEY",    valueFrom = aws_ssm_parameter.adzuna_app_key.arn },
      { name = "ANTHROPIC_API_KEY", valueFrom = aws_ssm_parameter.anthropic_api_key.arn },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.backend.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "backend"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/api/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
}

resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "backend" {
  name        = "${var.app_name}-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/health"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

resource "aws_ecs_service" "backend" {
  name            = "${var.app_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.backend.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true   # auto-rollback if new deploy is unhealthy
  }

  depends_on = [aws_lb_listener.http]
}

# Auto-scaling for ECS service
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = 8
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${var.app_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
