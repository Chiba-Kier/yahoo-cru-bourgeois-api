resource "aws_s3_bucket" "search_results" {
  bucket = "${var.project_name}-${var.environment}-results-${data.aws_caller_identity.current.account_id}"

  force_destroy = var.environment == "dev" ? true : false

  tags = {
    Name = "${var.project_name}-results"
  }
}

resource "aws_s3_bucket_public_access_block" "search_results" {
  bucket = aws_s3_bucket.search_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}
