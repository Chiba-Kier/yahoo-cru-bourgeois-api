# ビルドディレクトリの作成と依存関係のインストール
resource "null_resource" "lambda_build" {
  triggers = {
    requirements = filesha256("${path.module}/../requirements.txt")
    main_py      = filesha256("${path.module}/../main.py")
    modules      = sha256(join("", [for f in fileset("${path.module}/../modules", "**") : filesha256("${path.module}/../modules/${f}")]))
    # WSLへの切り替えをトリガーにする
    build_version = "20240318-wsl-v1" 
  }

  provisioner "local-exec" {
    working_dir = path.module
    # WSLを使用してLinuxネイティブのビルドを行う
    interpreter = ["wsl", "bash", "-c"]
    command     = <<EOT
      set -e
      echo "Starting build in WSL..."
      
      # 1. ビルドディレクトリのリセット
      rm -rf build && mkdir -p build
      
      # 2. 依存ライブラリのインストール
      # WSL側に python3 および python3-pip がインストールされている必要があります
      python3 -m pip install -t build -r ../requirements.txt --upgrade
      
      # 3. ソースコードのコピー
      cp ../main.py build/
      cp -r ../modules build/
      cp -r ../data build/
      
      # 4. 不要なファイルの削除
      find build -name "__pycache__" -type d -exec rm -rf {} +
      find build -name "*.pyc" -delete
      
      echo "Build completed successfully."
    EOT
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
resource "aws_lambda_function" "search_wine" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "main.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.10"
  timeout          = 900 # 15 minutes
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

# CloudWatch Logs for Lambda
resource "aws_cloudwatch_log_group" "lambda_log" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}
