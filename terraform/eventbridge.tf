# EventBridgeによる定期実行
resource "aws_cloudwatch_event_rule" "scheduled_search" {
  name                = "${var.project_name}-schedule"
  description         = "Daily scheduled search for wine classifications"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.scheduled_search.name
  target_id = "SearchWineLambda"
  arn       = aws_lambda_function.search_wine.arn
  
  # Trigger for "all" classifications by default
  input = jsonencode({
    classification = null
  })
}

# Lambdaに対するEventBridgeからの呼び出し許可
resource "aws_iam_role_policy" "lambda_invoke_permission" {
  name = "${var.project_name}-lambda-invoke-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.search_wine.arn
      }
    ]
  })
}

# Alternative: Using aws_lambda_permission (usually preferred for EventBridge)
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.search_wine.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_search.arn
}
