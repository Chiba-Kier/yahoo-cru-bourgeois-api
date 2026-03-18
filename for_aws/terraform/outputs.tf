output "s3_bucket_name" {
  description = "Name of the S3 bucket where results are stored"
  value       = aws_s3_bucket.search_results.id
}

output "collector_lambda_arn" {
  description = "ARN of the Collector Lambda function"
  value       = aws_lambda_function.collector.arn
}

output "reader_lambda_arn" {
  description = "ARN of the Reader Lambda function"
  value       = aws_lambda_function.reader.arn
}

output "reader_url" {
  description = "URL of the Reader Lambda Function (Public)"
  value       = aws_lambda_function_url.reader_url.function_url
}
