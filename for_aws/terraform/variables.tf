variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "yahoo-cru-bourgeois"
}

variable "environment" {
  description = "Environment (dev or prod)"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "wine-classification-search"
}

variable "classifications" {
  description = "List of wine classifications to search"
  type        = list(string)
  default     = ["medoc", "cru_bourgeois", "cru_bourgeois_top", "medoc_second_third"]
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "yahoo-cru-bourgeois-search-api"
}

variable "schedule_expression" {
  description = "Cron or rate expression for the EventBridge rule"
  type        = string
  default     = "cron(0 0 ? * 5 *)" # 毎週金曜日0時(UTC)に実行
}

variable "yahoo_api_key" {
  description = "Yahoo! Shopping API Key"
  type        = string
  sensitive   = true
}
