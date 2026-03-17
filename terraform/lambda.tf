# ビルドディレクトリの作成と依存関係のインストール
resource "null_resource" "lambda_build" {
  triggers = {
    requirements = filesha256("${path.module}/../requirements.txt")
    main_py      = filesha256("${path.module}/../main.py")
    modules      = sha256(join("", [for f in fileset("${path.module}/../modules", "**") : filesha256("${path.module}/../modules/${f}")]))
  }

  provisioner "local-exec" {
    command = <<EOT
      if (Test-Path "${path.module}/build") { Remove-Item -Recurse -Force "${path.module}/build" }
      New-Item -ItemType Directory -Path "${path.module}/build"
      
      # 1. 依存ライブラリのインストール
      pip install -r "${path.module}/../requirements.txt" -t "${path.module}/build"
      
      # 2. ソースコードのコピー
      Copy-Item -Path "${path.module}/../main.py" -Destination "${path.module}/build/"
      Copy-Item -Path "${path.module}/../modules" -Destination "${path.module}/build/" -Recurse
      Copy-Item -Path "${path.module}/../data" -Destination "${path.module}/build/" -Recurse
      
      # 3. 不要なファイルの削除（キャッシュ等）
      Get-ChildItem -Path "${path.module}/build" -Include "__pycache__", "*.pyc" -Recurse | Remove-Item -Recurse -Force
    EOT
    interpreter = ["powershell", "-Command"]
  }
}

# Lambda関数のコードをZIP化
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/build"
  output_path = "${path.module}/lambda_function.zip"
  
  depends_on = [null_resource.lambda_build]
}

# AWS Managed Layer for Pandas (ap-northeast-1)
# Note: The ARN might change, but this is a common one for Python 3.10
resource "aws_lambda_function" "search_wine" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "main.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.10"
  timeout          = 900 # 15 minutes (as per design)
  memory_size      = 512 # Sufficient for pandas

  layers = [
    "arn:aws:lambda:ap-northeast-1:336392948345:layer:AWSSDKPandas-Python310:3" # Example ARN
  ]

  environment {
    variables = {
      ENV              = var.environment
      S3_BUCKET_NAME   = aws_s3_bucket.search_results.id
      YAHOO_CLIENT_ID  = var.yahoo_api_key
    }
  }
}

# CloudWatch Logs for Lambda
resource "aws_cloudwatch_log_group" "lambda_log" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}
