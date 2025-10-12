#!/usr/bin/env python3
"""
Deploy GitHub OIDC provider and IAM role for GitHub Actions.

This is a one-time setup script. Run this before using GitHub Actions deployment:
    python setup_github_oidc.py YOUR_GITHUB_ORG YOUR_GITHUB_REPO

Example:
    python setup_github_oidc.py myusername learn-aws-eventbridge
"""
import sys

import aws_cdk as cdk

from github_oidc_stack import GitHubOIDCStack

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python setup_github_oidc.py <github-org> <github-repo>")
        print("Example: python setup_github_oidc.py myusername learn-aws-eventbridge")
        sys.exit(1)

    github_org = sys.argv[1]
    github_repo = sys.argv[2]

    app = cdk.App()
    GitHubOIDCStack(app, "GitHubOIDCStack", github_org=github_org, github_repo=github_repo)

    app.synth()
