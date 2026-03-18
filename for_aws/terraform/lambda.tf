# Lambda用のビルドディレクトリ作成
resource "null_resource" "collector_build" {
  triggers = {
    handler      = filesha256("${path.module}/../collector/handler.py")
    modules      = sha256(join("", [for f in fileset("${path.module}/../modules", "**") : filesha256("${path.module}/../modules/${f}")]))
    requirements = filesha256("${path.module}/../../requirements.txt")
  }

  provisioner "local-exec" {
    working_dir = path.module
    interpreter = ["/bin/bash", "-c"]
    command     = <<EOT
      set -e
      rm -rf build_collector && mkdir -p build_collector
      cp ../collector/handler.py build_collector/
      cp -r ../modules build_collector/
      # 必要に応じて以下を有効化
      # python3 -m pip install -t build_collector -r ../../requirements.txt
      echo "Collector build completed."
    EOT
  }
}

resource "null_resource" "reader_build" {
  triggers = {
    handler      = filesha256("${path.module}/../reader/handler.py")
    modules      = sha256(join("", [for f in fileset("${path.module}/../modules", "**") : filesha256("${path.module}/../modules/${f}")]))
    requirements = filesha256("${path.module}/../../requirements.txt")
  }

  provisioner "local-exec" {
    working_dir = path.module
    interpreter = ["/bin/bash", "-c"]
    command     = <<EOT
      set -e
      rm -rf build_reader && mkdir -p build_reader
      cp ../reader/handler.py build_reader/
      cp -r ../modules build_reader/
      # 必要に応じて以下を有効化
      # python3 -m pip install -t build_reader -r ../../requirements.txt
      echo "Reader build completed."
    EOT
  }
}

# ZIP化
data "archive_file" "collector_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build_collector"
  output_path = "${path.module}/collector.zip"
  depends_on  = [null_resource.collector_build]
}

data "archive_file" "reader_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build_reader"
  output_path = "${path.module}/reader.zip"
  depends_on  = [null_resource.reader_build]
}

# Collector Lambda (EventBridge triggered)
resource "aws_lambda_function" "collector" {
  filename         = data.archive_file.collector_zip.output_path
  function_name    = "${var.project_name}-collector"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.collector_zip.output_base64sha256
  runtime          = "python3.10"
  timeout          = 900
  memory_size      = 512

  layers = [
    "arn:aws:lambda:ap-northeast-1:336392948345:layer:AWSSDKPandas-Python310:3"
  ]

  environment {
    variables = {
      ENV              = var.environment
      S3_BUCKET_NAME   = aws_s3_bucket.search_results.id
      YAHOO_CLIENT_ID  = var.yahoo_api_key
    }
  }
}

# Reader Lambda (HTTP triggered)
resource "aws_lambda_function" "reader" {
  filename         = data.archive_file.reader_zip.output_path
  function_name    = "${var.project_name}-reader"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.reader_zip.output_base64sha256
  runtime          = "python3.10"
  timeout          = 30
  memory_size      = 256

  layers = [
    "arn:aws:lambda:ap-northeast-1:336392948345:layer:AWSSDKPandas-Python310:3"
  ]

  environment {
    variables = {
      ENV              = var.environment
      S3_BUCKET_NAME   = aws_s3_bucket.search_results.id
    }
  }
}

# Reader用のLambda Function URL (API Gatewayの代わり)
resource "aws_lambda_function_url" "reader_url" {
  function_name      = aws_lambda_function.reader.function_name
  authorization_type = "NONE"
  cors {
    allow_origins = ["*"]
    allow_methods = ["GET"]
  }
}
