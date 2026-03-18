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
  description = "Yahoo! Shopping API Key (Application ID)"
  type        = string
  sensitive   = true
}

variable "custom_domain_name" {
  description = "The custom domain name for the Reader API (e.g., api.example.com)"
  type        = string
  default     = ""
}

variable "route53_zone_id" {
  description = "The Route 53 Hosted Zone ID for the domain"
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "The ARN of the ACM certificate for the custom domain (must be in the same region)"
  type        = string
  default     = ""
}
