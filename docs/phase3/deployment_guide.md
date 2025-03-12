# Phase 3: AWS Deployment Guide

This guide provides best practices and troubleshooting steps for deploying the WhatsApp chatbot to AWS. It is designed to prevent common deployment issues and ensure a smooth continuous development process.

## Bootstrap Management

The CDK bootstrap process creates resources that CDK needs for deployment, including an S3 bucket for assets and IAM roles. This is a one-time setup per AWS account and region.

### Important Bootstrap Rules

- ⚠️ **Bootstrap only ONCE per AWS account/region**
- ⚠️ **Never run bootstrap commands again** unless setting up in a new region
- ✅ **Bootstrap completed on:** March 11, 2025 for account 650251723700 in region eu-north-1

### Bootstrap Command (Reference Only - DO NOT RUN AGAIN)

```bash
cdk bootstrap aws://650251723700/eu-north-1
```

## Standard Deployment Workflow

For all future deployments, follow this workflow:

```bash
# Navigate to CDK directory
cd src/cdk

# Review changes before deploying (ALWAYS do this first)
cdk diff

# Deploy changes if the diff looks correct
cdk deploy
```

## CDK Deployment Optimization

To make deployments faster and more reliable, consider these optimization techniques:

### 1. Use `cdk diff` Before Every Deployment

Always run `cdk diff` before deploying to preview changes:

```bash
cd src/cdk
cdk diff --app "python app.py"
```

**Benefits:**
- Catches potential issues before deployment
- Shows exactly what resources will be modified
- Helps prevent failed deployments and rollbacks
- Provides an opportunity to verify that changes match your intentions

### 2. Use `--hotswap` for Lambda Code Changes

For Lambda function code updates that don't change infrastructure:

```bash
cd src/cdk
cdk deploy --hotswap --app "python app.py"
```

**Benefits:**
- Much faster than full CloudFormation deployments (seconds vs. minutes)
- Bypasses CloudFormation for simple code changes
- Ideal for iterative development and testing
- Reduces deployment time by up to 90% for code-only changes

**When to use:**
- Only for Lambda code changes
- Not for infrastructure changes (API Gateway, IAM roles, etc.)
- Not for production deployments where you want full tracking

### 3. Deploy in Smaller Stacks (For Larger Applications)

For complex applications, consider splitting into multiple stacks:

```bash
# Example structure
- infrastructure-stack (VPC, subnets, security groups)
- database-stack (RDS, DynamoDB)
- application-stack (Lambda, API Gateway)
- monitoring-stack (CloudWatch alarms, dashboards)
```

**Benefits:**
- Isolates failures to specific components
- Speeds up deployments for individual components
- Makes rollbacks more targeted and less disruptive
- Improves team collaboration on different parts of the system

### 4. Use Specific Stack Selection for Targeted Deployments

Deploy only specific stacks when working on a subset of the application:

```bash
cdk deploy ApplicationStack --app "python app.py"
```

**Note:** Our current application uses a single stack, but this approach becomes valuable as the application grows.

## Lambda Function Updates

If you only need to update the Lambda function code without changing infrastructure:

```bash
# Package the Lambda function
cd src/lambda
zip -r ../../lambda_function.zip .

# Update the Lambda function code
aws lambda update-function-code \
  --function-name urmston-town-registration-whatsapp \
  --zip-file fileb://../../lambda_function.zip \
  --region eu-north-1
```

## Environment Variable Management

### Viewing Current Environment Variables

```bash
# View Lambda environment variables
aws lambda get-function-configuration \
  --function-name urmston-town-registration-whatsapp \
  --region eu-north-1 \
  --query 'Environment.Variables'
```

### Updating SSM Parameters

```bash
# Update an SSM parameter
aws ssm put-parameter \
  --name "/urmston/twilio/phone-number" \
  --value "whatsapp:+447700148000" \
  --type "String" \
  --overwrite \
  --region eu-north-1
```

### Updating Secrets in AWS Secrets Manager

```bash
# Update a secret
aws secretsmanager update-secret \
  --secret-id urmston/twilio/account-sid \
  --secret-string "YOUR_NEW_TWILIO_ACCOUNT_SID" \
  --region eu-north-1
```

## Troubleshooting Guide

### Common Deployment Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Resource already exists" | CDK trying to create a resource that already exists | Use `cdk diff` to identify conflicts and modify your CDK code |
| "Access denied" | Insufficient IAM permissions | Verify IAM permissions for the user/role being used |
| "ROLLBACK_COMPLETE" | Previous deployment failed | Check CloudFormation logs for the specific error |
| "Bucket already exists" | S3 bucket name conflict | Use a different bucket name or delete the existing bucket if not in use |

### Checking CloudFormation Logs

```bash
# List recent stack events
aws cloudformation describe-stack-events \
  --stack-name urmston-town-registration-stack \
  --region eu-north-1 \
  --max-items 10
```

### Checking Lambda Logs

```bash
# Get the most recent log stream
LATEST_STREAM=$(aws logs describe-log-streams \
  --log-group-name /aws/lambda/urmston-town-registration-whatsapp \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query 'logStreams[0].logStreamName' \
  --output text \
  --region eu-north-1)

# View logs from that stream
aws logs get-log-events \
  --log-group-name /aws/lambda/urmston-town-registration-whatsapp \
  --log-stream-name $LATEST_STREAM \
  --limit 20 \
  --region eu-north-1
```

## Bootstrap Recovery Procedure (EMERGENCY USE ONLY)

If you encounter unresolvable bootstrap issues, follow these steps as a last resort:

1. **Delete the existing bootstrap stack**:
   ```bash
   aws cloudformation delete-stack --stack-name CDKToolkit --region eu-north-1
   aws cloudformation wait stack-delete-complete --stack-name CDKToolkit --region eu-north-1
   ```

2. **Manually clean up any orphaned resources**:
   - Delete the S3 bucket `cdk-hnb659fds-assets-650251723700-eu-north-1` through the AWS Console
   - Check for and delete any IAM roles with names starting with `cdk-`

3. **Bootstrap again**:
   ```bash
   cdk bootstrap aws://650251723700/eu-north-1
   ```

## Rollback Procedures

### Rolling Back to a Previous Version

If a deployment introduces issues:

1. **Identify the last working version** in your Git repository
2. **Check out that version**:
   ```bash
   git checkout <commit-hash>
   ```
3. **Deploy the previous version**:
   ```bash
   cd src/cdk
   cdk deploy
   ```

### Recovering from Failed Deployments

If a deployment fails and leaves the stack in an inconsistent state:

1. **Check the CloudFormation console** for the specific error
2. **Fix the issue** in your CDK code
3. **Try deploying again** with `cdk deploy`
4. If still failing, consider **destroying and recreating** the stack:
   ```bash
   cdk destroy
   cdk deploy
   ```
   ⚠️ **Warning**: This will delete all resources in the stack. Ensure you have backups of any important data.

## Testing After Deployment

Always verify your deployment with these tests:

1. **Test the trigger endpoint**:
   ```bash
   curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
   -H "Content-Type: application/json" \
   -H "x-api-key: YOUR_API_KEY_HERE" \
   -d @testing/payloads/test_payload.json
   ```

2. **Check CloudWatch logs** to confirm the function executed correctly

3. **Verify WhatsApp message delivery** on the test phone number

## Security Best Practices

1. **Never commit credentials** to Git
2. **Rotate API keys** periodically
3. **Use least privilege IAM policies**
4. **Enable CloudTrail** for auditing
5. **Review security groups** to ensure minimal necessary access

## Monitoring and Alerting

1. **Set up CloudWatch alarms** for:
   - Lambda errors
   - API Gateway 4xx/5xx errors
   - SQS queue depth

2. **Create a dashboard** for key metrics:
   ```bash
   aws cloudwatch put-dashboard \
     --dashboard-name "UrmstonTownRegistration" \
     --dashboard-body file://monitoring/dashboard.json \
     --region eu-north-1
   ```

## Conclusion

Following these deployment practices will help ensure smooth, reliable deployments of the WhatsApp chatbot. Always test thoroughly after deployment and maintain good documentation of any issues encountered and their solutions.

Remember: The goal is to make deployments boring and predictable! 