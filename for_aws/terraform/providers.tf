terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWSプロバイダーの設定
provider "aws" {
  region  = "ap-northeast-1" # 東京リージョン
  profile = "default"        # aws configureで設定するプロファイル名

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
    }
  }
}
