output "s3_bucket_name" {
  description = "Name of the S3 bucket where results are stored"
  value       = aws_s3_bucket.search_results.id
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.search_wine.arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.scheduled_search.arn
}
