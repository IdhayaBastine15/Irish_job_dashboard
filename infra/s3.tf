resource "aws_s3_bucket" "resumes" {
  bucket = "${var.app_name}-resumes-${var.env}"
  tags   = { Name = "${var.app_name}-resumes" }
}

resource "aws_s3_bucket_versioning" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "resumes" {
  bucket                  = aws_s3_bucket.resumes.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
