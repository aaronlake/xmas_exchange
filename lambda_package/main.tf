provider "aws" {
  region = "us-east-2" # Replace with your preferred region
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "secret_santa_lambda_role"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "secret_santa_function" {
  function_name    = "SecretSantaFunction"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      ENCRYPTION_KEY = var.encryption_key
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "secret_santa_api" {
  name        = "SecretSantaAPI"
  description = "API for Secret Santa Lambda Function"
}

resource "aws_api_gateway_resource" "code_resource" {
  rest_api_id = aws_api_gateway_rest_api.secret_santa_api.id
  parent_id   = aws_api_gateway_rest_api.secret_santa_api.root_resource_id
  path_part   = "code"
}

resource "aws_api_gateway_method" "get_method" {
  rest_api_id   = aws_api_gateway_rest_api.secret_santa_api.id
  resource_id   = aws_api_gateway_resource.code_resource.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.code" = true
  }
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.secret_santa_api.id
  resource_id             = aws_api_gateway_resource.code_resource.id
  http_method             = aws_api_gateway_method.get_method.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.secret_santa_function.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_santa_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.secret_santa_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]

  rest_api_id = aws_api_gateway_rest_api.secret_santa_api.id
  stage_name  = "prod"
}

# Outputs
output "api_invoke_url" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}/prod/code"
}
