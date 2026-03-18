output "s3_bucket_name" {
  description = "Name of the S3 bucket where results are stored"
  value       = aws_s3_bucket.search_results.id
}

output "reader_api_gateway_url" {
  description = "The URL of the API Gateway for the Reader"
  value       = aws_apigatewayv2_api.reader_api.api_endpoint
}

output "collector_lambda_arn" {
  description = "ARN of the Collector Lambda function"
  value       = aws_lambda_function.collector.arn
}
