resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "postgres" {
  identifier        = "${var.app_name}-postgres"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"   # free-tier eligible
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "irish_jobs"
  username = "postgres"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 7
  multi_az                = false   # set true for production HA

  tags = { Name = "${var.app_name}-postgres" }
}
