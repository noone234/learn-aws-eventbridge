"""CDK Stack for GitHub Actions OIDC Provider and IAM Role."""
from typing import Any

from aws_cdk import Duration, Stack, aws_iam as iam
from constructs import Construct


class GitHubOIDCStack(Stack):
    """
    CDK Stack that creates an OIDC provider and IAM role for GitHub Actions.

    This allows GitHub Actions to assume an AWS IAM role without storing
    long-lived credentials in GitHub secrets.
    """

    def __init__(
        self, scope: Construct, construct_id: str, github_org: str, github_repo: str, **kwargs: Any
    ) -> None:
        """
        Initialize the GitHub OIDC Stack.

        Args:
            scope: CDK app scope
            construct_id: Unique identifier for this stack
            github_org: GitHub organization or username (e.g., "myorg")
            github_repo: GitHub repository name (e.g., "learn-aws-eventbridge")
            **kwargs: Additional stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create GitHub OIDC provider
        github_provider = iam.OpenIdConnectProvider(
            self,
            "GitHubOIDCProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
        )

        # Create IAM role for GitHub Actions
        github_role = iam.Role(
            self,
            "GitHubActionsRole",
            role_name="GitHubActionsDeploymentRole",
            assumed_by=iam.FederatedPrincipal(
                github_provider.open_id_connect_provider_arn,
                {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*",
                    },
                },
                "sts:AssumeRoleWithWebIdentity",
            ),
            description="Role for GitHub Actions to deploy CDK stacks",
            max_session_duration=Duration.hours(1),
        )

        # Add permissions for CDK deployments
        # Note: For a demo, we use broad permissions. In production, narrow these down.
        github_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        # Output the role ARN for use in GitHub Actions
        from aws_cdk import CfnOutput

        CfnOutput(
            self,
            "GitHubActionsRoleArn",
            value=github_role.role_arn,
            description="IAM Role ARN for GitHub Actions",
            export_name="GitHubActionsRoleArn",
        )
