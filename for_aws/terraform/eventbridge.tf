# 格付けごとのEventBridgeルール作成
resource "aws_cloudwatch_event_rule" "scheduled_search" {
  for_each            = toset(var.classifications)
  name                = "${var.project_name}-${each.key}-schedule"
  description         = "Weekly scheduled search for ${each.key}"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  for_each  = toset(var.classifications)
  rule      = aws_cloudwatch_event_rule.scheduled_search[each.key].name
  target_id = "CollectorLambda-${each.key}"
  arn       = aws_lambda_function.collector.arn
  
  input = jsonencode({
    classification = each.key
  })
}

# Lambdaに対するEventBridgeからの呼び出し許可
resource "aws_lambda_permission" "allow_eventbridge" {
  for_each      = toset(var.classifications)
  statement_id  = "AllowExecutionFromEventBridge-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.collector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_search[each.key].arn
}
