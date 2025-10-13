# Deploy Checklist

Pre-deployment checklist and deployment commands.

## One-Time Setup

### 1. GitHub OIDC Provider (if using GitHub Actions)
```bash
python infrastructure/setup_github_oidc.py <github-org> <github-repo>
cdk deploy --app "python infrastructure/setup_github_oidc.py <github-org> <github-repo>"
```

This creates:
- GitHub OIDC provider in IAM
- GitHubActionsDeploymentRole with deployment permissions

### 2. GitHub Secrets (if using GitHub Actions)
Add these secrets to your GitHub repository:
- `AWS_ROLE_ARN`: ARN of GitHubActionsDeploymentRole (from above)
- `AWS_REGION`: Your AWS region (e.g., us-east-1)

## Pre-Deployment Checklist

- [ ] Run quality checks: `ruff check --fix .`
- [ ] Run formatting: `black .`
- [ ] Run type checking: `mypy .`
- [ ] Run tests: `pytest`
- [ ] All tests passing (13 tests expected)
- [ ] Git status clean or changes committed
- [ ] Review CloudFormation changeset carefully

## Deployment Commands

### Bootstrap CDK (First Time Only)
```bash
cdk bootstrap
```

### Synthesize CloudFormation Template
```bash
cdk synth
```

Review the generated template in `cdk.out/OrderProcessingStack.template.json`

### Deploy
```bash
cdk deploy
```

**Important**: Review the changeset and approve when prompted.

### Deploy Without Approval (CI/CD)
```bash
cdk deploy --require-approval never
```

## Post-Deployment

### 1. Get API Endpoint
```bash
aws cloudformation describe-stacks \
  --stack-name OrderProcessingStack \
  --query 'Stacks[0].Outputs[?OutputKey==`OrdersApiEndpoint`].OutputValue' \
  --output text
```

### 2. Test API
```bash
curl -X POST <api-endpoint>/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "test-123", "purpose": "new-order"}'
```

Expected response: `{"message": "Order received and processing"}`

### 3. Check CloudWatch Logs
Verify all components are logging:
- `/aws/apigateway/public-api-access`
- `/aws/lambda/order-receiver`
- `/aws/events/route-to-notifier`
- `/aws/events/route-to-inventory`
- `/aws/events/route-to-document`
- `/aws/lambda/notifier`
- `/aws/lambda/inventory`
- `/aws/lambda/document`

### 4. Subscribe to Alarms
```bash
aws sns subscribe \
  --topic-arn <alarm-topic-arn> \
  --protocol email \
  --notification-endpoint your-email@example.com
```

Confirm the subscription via email.

## Destroy Stack (Cleanup)
```bash
cdk destroy
```

**Warning**: This will delete all resources including logs.

## Troubleshooting

### CDK Deploy Fails
- Check AWS credentials: `aws sts get-caller-identity`
- Ensure CDK is bootstrapped: `cdk bootstrap`
- Check for resource limits (Lambda, API Gateway, etc.)

### Lambda Errors After Deployment
- Check Lambda logs in CloudWatch
- Verify IAM permissions (event bus access, SQS access)
- Test with minimal payload first

### API Gateway 403 Error
- Verify you're using the correct URL path: `/prod/orders`
- Check API Gateway logs for details
