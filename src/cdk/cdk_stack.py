from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations,
    aws_logs as logs,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_cloudwatch as cloudwatch,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)
from constructs import Construct

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create SQS queue for webhook messages
        webhook_queue = sqs.Queue(
            self, "WebhookQueue",
            visibility_timeout=Duration.seconds(300),  # 5 minutes
            retention_period=Duration.days(1)
        )
        
        # Get configuration from SSM Parameter Store
        twilio_phone_number = ssm.StringParameter.from_string_parameter_name(
            self, "TwilioPhoneNumber",
            string_parameter_name="/urmston/twilio/phone-number"
        ).string_value
        
        twilio_template_sid = ssm.StringParameter.from_string_parameter_name(
            self, "TwilioTemplateSid",
            string_parameter_name="/urmston/twilio/template-sid"
        ).string_value
        
        # Create Lambda function
        registration_lambda = _lambda.Function(
            self, "RegistrationHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../lambda"),
            handler="app.lambda_handler",
            memory_size=256,
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "WEBHOOK_QUEUE_URL": webhook_queue.queue_url,
                "TWILIO_ACCOUNT_SID": secretsmanager.Secret.from_secret_name_v2(
                    self, "TwilioAccountSid", "urmston/twilio/account-sid"
                ).secret_value.to_string(),
                "TWILIO_AUTH_TOKEN": secretsmanager.Secret.from_secret_name_v2(
                    self, "TwilioAuthToken", "urmston/twilio/auth-token"
                ).secret_value.to_string(),
                "TWILIO_PHONE_NUMBER": twilio_phone_number,
                "TWILIO_TEMPLATE_SID": twilio_template_sid
            }
        )
        
        # Grant Lambda permission to send messages to SQS
        webhook_queue.grant_send_messages(registration_lambda)
        
        # Create SQS event source for Lambda
        webhook_event_source = lambda_event_sources.SqsEventSource(
            webhook_queue,
            batch_size=10,
            max_batching_window=Duration.seconds(30)
        )
        registration_lambda.add_event_source(webhook_event_source)
        
        # Create HTTP API (more cost-effective than REST API)
        lambda_integration = apigwv2_integrations.HttpLambdaIntegration(
            "LambdaIntegration", registration_lambda
        )
        
        api = apigwv2.HttpApi(
            self, "RegistrationApi",
            default_integration=lambda_integration
        )
        
        # Create API key and usage plan using REST API (HTTP API doesn't support API keys)
        rest_api = apigw.RestApi(
            self, "RegistrationRestApi",
            deploy=True,
            deploy_options=apigw.StageOptions(
                stage_name="prod"
            )
        )
        
        # Create Lambda integrations for REST API
        rest_lambda_integration = apigw.LambdaIntegration(registration_lambda)
        
        # Add routes to REST API
        trigger_resource = rest_api.root.add_resource("trigger")
        trigger_method = trigger_resource.add_method(
            "POST", 
            rest_lambda_integration,
            api_key_required=True
        )
        
        webhook_resource = rest_api.root.add_resource("webhook")
        webhook_method = webhook_resource.add_method(
            "POST", 
            rest_lambda_integration
        )
        
        # Create API key
        api_key = apigw.ApiKey(
            self, "RegistrationApiKey",
            api_key_name="UrmstonTownRegistrationKey",
            enabled=True
        )
        
        # Create usage plan for trigger endpoint with higher limits for bulk invitations
        trigger_usage_plan = rest_api.add_usage_plan(
            "TriggerUsagePlan",
            name="TriggerEndpointPlan",
            throttle=apigw.ThrottleSettings(
                rate_limit=25,  # 25 requests per second to handle bulk invitations
                burst_limit=50  # 50 requests in burst
            )
        )
        
        # Add stage to usage plan
        trigger_usage_plan.add_api_stage(
            stage=rest_api.deployment_stage
        )
        
        # Associate API key with usage plan
        trigger_usage_plan.add_api_key(api_key)
        
        # Create CloudWatch alarms for monitoring
        
        # API throttling alarm
        throttling_alarm = cloudwatch.Alarm(
            self, "ApiThrottlingAlarm",
            metric=rest_api.metric_count(),
            threshold=10,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Alarm if API throttling exceeds 10 in 1 minute",
            alarm_name="ApiThrottlingAlarm"
        )
        
        # Lambda errors alarm
        error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            metric=registration_lambda.metric_errors(),
            threshold=5,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Alarm if Lambda errors exceed 5 in 1 minute",
            alarm_name="LambdaErrorAlarm"
        ) 