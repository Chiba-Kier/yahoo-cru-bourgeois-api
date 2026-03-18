# HTTP API Gateway
resource "aws_apigatewayv2_api" "reader_api" {
  name          = "${var.project_name}-reader-api"
  protocol_type = "HTTP"
  # CORS configuration removed to let Lambda handle it
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "reader_lambda_integration" {
  api_id           = aws_apigatewayv2_api.reader_api.id
  integration_type = "AWS_PROXY"

  integration_uri    = aws_lambda_function.reader.invoke_arn
  payload_format_version = "2.0"
}

# Route Definition
resource "aws_apigatewayv2_route" "search_route" {
  api_id    = aws_apigatewayv2_api.reader_api.id
  route_key = "GET /search/{classification}"
  target    = "integrations/${aws_apigatewayv2_integration.reader_lambda_integration.id}"
}

# Default Stage (auto-deploy)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.reader_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "apigw_reader_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reader.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.reader_api.execution_arn}/*/*"
}

# --- Route 53 Custom Domain (Conditional) ---
# Active when custom_domain_name is provided.
resource "aws_apigatewayv2_domain_name" "reader_custom_domain" {
  count       = var.custom_domain_name != "" ? 1 : 0
  domain_name = var.custom_domain_name

  domain_name_configuration {
    certificate_arn = var.acm_certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "reader_mapping" {
  count       = var.custom_domain_name != "" ? 1 : 0
  api_id      = aws_apigatewayv2_api.reader_api.id
  domain_name = aws_apigatewayv2_domain_name.reader_custom_domain[0].id
  stage       = aws_apigatewayv2_stage.default.id
}

resource "aws_route53_record" "api_record" {
  count   = (var.custom_domain_name != "" && var.route53_zone_id != "") ? 1 : 0
  name    = var.custom_domain_name
  type    = "A"
  zone_id = var.route53_zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.reader_custom_domain[0].domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.reader_custom_domain[0].domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
