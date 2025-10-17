# CI/CD Pipeline Flow

This document illustrates the flow of the CI/CD pipeline for the Aladdin Ventures monorepo, from code changes to production deployment.

## Pipeline Overview

The pipeline is orchestrated by the `.github/workflows/ci-cd.yml` workflow and is composed of three main stages: Continuous Integration (CI), Continuous Delivery to Staging, and Continuous Deployment to Production.

## Visual Flow Diagram

```mermaid
graph TD
    A[Developer Pushes Code or Creates PR] --> B{CI/CD Orchestrator};

    B --> C{CI Workflow};
    C --> D{Detect Changed Projects};
    D --> E[Build, Test, Lint];
    E --> F{Security Scan};
    F --> G{CI Success?};

    G -- Yes --> H{Staging Deployment};
    H --> I[Deploy to Staging];
    I --> J{Smoke & E2E Tests};
    J --> K{Staging Success?};

    G -- No --> L[Notify Failure];

    K -- Yes & branch == 'main' --> M{Production Deployment (Manual Approval)};
    M --> N[Deploy to Production];
    N --> O{Post-Deployment Verification};
    O --> P{Production Success?};

    K -- No --> L;
    P -- No --> L;
    P -- Yes --> Q[Notify Success];

    subgraph "Continuous Integration"
        C
        D
        E
        F
    end

    subgraph "Continuous Delivery (Staging)"
        H
        I
        J
    end

    subgraph "Continuous Deployment (Production)"
        M
        N
        O
    end
```

## Stage Details

### 1. Continuous Integration (CI)

*   **Trigger**: A push to `main` or `develop` branches, or a pull request targeting these branches.
*   **Workflow**: `.github/workflows/ci.yml`
*   **Key Steps**:
    1.  **Detect Changes**: The `scripts/detect_changes.py` script identifies which applications or packages have been modified.
    2.  **AI Validation**: The `ai-tools/ai_validate.py` script summarizes the changes and provides a risk assessment.
    3.  **Matrix Build**: A parallel build and test job is dynamically created for each affected project.
    4.  **Lint & Test**: Code is linted and unit/integration tests are run.
    5.  **Build**: Deployable artifacts (e.g., Docker images) are built.
    6.  **Security Scan**: Vulnerability scans are performed on code and dependencies.

### 2. Continuous Delivery (Staging)

*   **Trigger**: Successful completion of the CI workflow on the `develop` or `main` branch.
*   **Workflow**: `.github/workflows/cd-staging.yml`
*   **Key Steps**:
    1.  **Deployment**: Artifacts are automatically deployed to the `staging` environment.
    2.  **Testing**: Smoke tests and End-to-End (E2E) tests are run against the staging deployment to ensure functionality.
    3.  **Notification**: A Slack notification is sent with the deployment status and the AI-generated summary.

### 3. Continuous Deployment (Production)

*   **Trigger**: Successful completion of the staging deployment (originating from the `main` branch) AND manual approval from a designated reviewer.
*   **Workflow**: `.github/workflows/cd-production.yml`
*   **Key Steps**:
    1.  **Manual Approval**: A required reviewer must approve the deployment in the GitHub `production` environment.
    2.  **Deployment**: Artifacts are deployed to the `production` environment, ideally using a zero-downtime strategy like blue/green or canary.
    3.  **Verification**: Post-deployment health checks are performed.
    4.  **Notification**: A Slack notification is sent with the deployment status.

### 4. Release Management

*   **Trigger**: Successful completion of the CI workflow on the `main` branch.
*   **Workflow**: `.github/workflows/release.yml`
*   **Key Steps**:
    1.  **Semantic Versioning**: `semantic-release` analyzes commit messages to determine the next version number.
    2.  **Changelog**: A `CHANGELOG.md` file is automatically updated.
    3.  **GitHub Release**: A new release is created on GitHub with the new version tag and release notes.

