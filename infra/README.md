# Infrastructure as Code (IaC)

This directory contains Infrastructure as Code (IaC) templates for provisioning and managing the infrastructure required by Aladdin Ventures applications. We support deployments to AWS and Railway.

## AWS (Terraform)

The `aws/` subdirectory contains Terraform configurations for deploying resources on Amazon Web Services. This includes:

*   **`main.tf`**: Main Terraform configuration defining AWS resources like VPCs, S3 buckets, and placeholder services.
*   **`variables.tf`**: Input variables for customizing deployments (e.g., region, environment).
*   **`outputs.tf`**: Output values from the deployed infrastructure.

### Usage (AWS)

To deploy or update AWS infrastructure:

1.  Ensure you have AWS credentials configured (e.g., via environment variables or AWS CLI).
2.  Navigate to the `infra/aws` directory.
3.  Initialize Terraform:
    ```bash
    terraform init
    ```
4.  Review the planned changes:
    ```bash
    terraform plan -var="environment=staging" -var="project_name=aladdin"
    ```
5.  Apply the changes:
    ```bash
    terraform apply -var="environment=staging" -var="project_name=aladdin"
    ```

## Railway

The `railway/` subdirectory contains configurations for deploying services on Railway.app. This typically involves a `railway.json` file that defines services, build commands, and environment variables.

### Usage (Railway)

To deploy or update Railway services:

1.  Ensure you have the Railway CLI installed and authenticated.
2.  Navigate to the root of your monorepo.
3.  Deploy using the `railway.json` configuration:
    ```bash
    railway up
    ```
    Or for specific environments:
    ```bash
    railway deploy --environment staging
    ```

## Important Notes

*   **Parameterization**: Infrastructure configurations are parameterized to support multiple environments (e.g., `staging`, `production`).
*   **Secrets**: Sensitive information (e.g., database passwords) should be managed via secure secrets management solutions (e.g., AWS Secrets Manager, GitHub Secrets, Railway Variables) and not hardcoded in IaC templates.
*   **Customization**: The provided templates are starting points. Customize them to fit the specific needs of each application and service within the monorepo.

