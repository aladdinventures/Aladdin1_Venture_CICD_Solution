# Environment Setup for CI/CD

This guide provides step-by-step instructions for configuring the necessary environments and secrets for the Aladdin Ventures monorepo CI/CD pipeline.

## 1. GitHub Environments

We use GitHub Environments to manage deployments to `staging` and `production`. These environments allow for protection rules and environment-specific secrets.

### Creating Environments

1.  **Navigate to your repository** on GitHub.
2.  Go to **Settings > Environments**.
3.  Click **New environment** and create an environment named `staging`.
4.  Repeat the process to create an environment named `production`.

### Configuring Protection Rules (for Production)

For the `production` environment, it is critical to add protection rules to prevent accidental deployments.

1.  In the `production` environment settings, enable **Required reviewers**.
2.  Add the appropriate teams or individuals who must approve production deployments.
3.  (Optional) Configure a **Wait timer** to add a delay before deployment.

## 2. Secrets Management

Sensitive information is managed using GitHub Secrets. We use a combination of repository-level and environment-level secrets.

### Required Secrets

The following secrets must be configured for the CI/CD pipeline to function correctly.

| Secret Name             | Scope                   | Description                                                                                              |
| :---------------------- | :---------------------- | :------------------------------------------------------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | `staging`, `production` | The AWS access key ID for the IAM user or role with permissions to deploy to the respective environment.   |
| `AWS_SECRET_ACCESS_KEY` | `staging`, `production` | The AWS secret access key for the IAM user or role.                                                      |
| `SLACK_WEBHOOK_URL`     | Repository              | The incoming webhook URL for your Slack workspace to receive pipeline notifications.                       |
| `GITHUB_TOKEN`          | Automatic (Repository)  | This is automatically provided by GitHub Actions. Ensure workflows have appropriate permissions to use it. |

### Setting Up Secrets

**For Environment Secrets (`staging` and `production`):**

1.  Go to **Settings > Environments** and select the environment (`staging` or `production`).
2.  Under **Environment secrets**, click **Add secret**.
3.  Add the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` with the appropriate values for that environment.

**For Repository Secrets:**

1.  Go to **Settings > Secrets and variables > Actions**.
2.  Under **Repository secrets**, click **New repository secret**.
3.  Add the `SLACK_WEBHOOK_URL`.

## 3. AWS Credentials and IAM

For security, it is crucial to follow the principle of least privilege when creating AWS credentials.

### Recommended IAM Setup

1.  **Create separate IAM users or roles** for `staging` and `production` environments. Do not use the same credentials for both.
2.  **Attach restrictive IAM policies** to these users/roles. Grant only the permissions necessary for deploying and managing the resources in that specific environment (e.g., permissions for ECS, S3, CloudFront, etc.).
3.  **Do not use your root AWS account** for CI/CD. Create dedicated IAM users.
4.  **Regularly rotate** your access keys as a security best practice.

### Example IAM Policy (for a simple S3 deployment)

This is a minimal example. Your actual policy will need to be more comprehensive based on the services you use.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-staging-bucket-name/*",
                "arn:aws:s3:::your-staging-bucket-name"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "*"
        }
    ]
}
```

Replace `your-staging-bucket-name` with the actual name of your S3 bucket for the staging environment. Create a similar but separate policy for production.

