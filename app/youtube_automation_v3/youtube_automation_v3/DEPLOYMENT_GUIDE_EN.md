# YouTube Automation System v3.0 - Deployment Guide

**Copyright © 2025 Saeed Alaediny. All rights reserved.**

This guide provides comprehensive instructions for deploying the YouTube Automation System v3.0 on a server, primarily focusing on a Docker-based setup. This version includes a robust core infrastructure, API endpoints, and stub implementations for content generation, video building, and uploading, allowing for end-to-end testing in a mock environment.

## 🎯 Project Overview

The YouTube Automation System v3.0 is designed as a modular, scalable platform for automated YouTube content generation and publishing. It leverages FastAPI for the API, SQLAlchemy for ORM, PostgreSQL for the database, Redis for caching and task queuing, and Celery for asynchronous task processing. The entire system is containerized using Docker and orchestrated with Docker Compose.

## 🚀 Quick Start (Docker Compose)

This is the recommended method for deployment, providing an isolated and easily manageable environment.

### Prerequisites

Ensure your server has the following installed:

- **Docker:** [Installation Guide](https://docs.docker.com/engine/install/)
- **Docker Compose:** [Installation Guide](https://docs.docker.com/compose/install/)

### Installation Steps

1.  **Transfer the Project:**
    Upload the `youtube_automation_v3.zip` package to your server. You can use `scp`, `rsync`, or any other secure file transfer method.

    ```bash
    # Example using scp (replace with your server details and local path)
    scp /path/to/local/youtube_automation_v3.zip ubuntu@your_server_ip:~/
    ```

2.  **Extract the Project:**
    SSH into your server and extract the project archive.

    ```bash
    ssh ubuntu@your_server_ip
    unzip ~/youtube_automation_v3.zip -d /home/ubuntu/
    cd /home/ubuntu/youtube_automation_v3
    ```

3.  **Configure Environment Variables:**
    The project uses environment variables for configuration. A template `.env.example` is provided.

    ```bash
    cp .env.example .env
    ```

    **Edit the `.env` file** using a text editor like `nano` or `vim`:

    ```bash
    nano .env
    ```

    **Key variables to configure:**

    -   `JWT_SECRET_KEY`: A strong, random string for JWT token signing. Generate one using `openssl rand -hex 32`.
    -   `SECRET_KEY`: Another strong, random string for general application security.
    -   `POSTGRES_PASSWORD`: Set a strong password for the PostgreSQL user.
    -   `REDIS_PASSWORD`: Set a strong password for Redis.
    -   `AI_PROVIDER`: Choose your AI provider (`ollama`, `openai`, `deepseek`). `ollama` is recommended for free local development.
        -   If `ollama`, configure `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
        -   If `openai` or `deepseek`, provide `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`.
    -   `LOG_LEVEL`: Set to `INFO` for production, `DEBUG` for development.
    -   `CORS_ORIGINS`: Adjust for your frontend application's domain (e.g., `http://localhost:3000,https://your-frontend.com`). Use `*` only for development.

4.  **Build and Start Services:**
    Navigate to the project root directory (`/home/ubuntu/youtube_automation_v3`) and use Docker Compose to build the images and start all services.

    ```bash
    docker compose build
    docker compose up -d
    ```

    -   `docker compose build`: Builds the Docker images for all services defined in `docker-compose.yml`.
    -   `docker compose up -d`: Starts the services in detached mode (runs in the background).

5.  **Verify Service Status:**
    Check if all containers are running correctly.

    ```bash
    docker compose ps
    ```

    You should see `Up` status for `web`, `db`, `redis`, `celery_worker`, and `celery_beat`.

6.  **Access the API:**
    The FastAPI application will be accessible on port `8000` of your server.

    -   **Health Check:** `http://your_server_ip:8000/health`
    -   **API Documentation (Swagger UI):** `http://your_server_ip:8000/docs`
    -   **API Documentation (ReDoc):** `http://your_server_ip:8000/redoc`

## 🔧 Configuration Details

Refer to the `.env.example` file for a complete list of configurable environment variables and their descriptions.

## 📊 Database Migrations (Alembic)

This project uses Alembic for database migrations. After the initial setup, if there are schema changes, you will need to run migrations.

1.  **Access the `web` service shell:**
    ```bash
    docker compose exec web bash
    ```

2.  **Run migrations:**
    ```bash
    alembic upgrade head
    ```

    *Note: For initial setup, `Base.metadata.create_all(bind=engine)` in `main.py` handles table creation. Alembic is for subsequent schema changes.* 

## 🐛 Troubleshooting

### Common Issues

-   **Container not starting:** Check logs for the specific service.
    ```bash
    docker compose logs <service_name>
    # Example: docker compose logs web
    ```

-   **`docker compose` command not found:** Ensure Docker Compose is installed correctly and in your PATH.

-   **`no configuration file provided`:** Ensure you are in the `youtube_automation_v3` directory or specify the `-f` flag (e.g., `docker compose -f docker-compose.yml up -d`).

-   **Database connection errors:** Verify `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` in your `.env` file and ensure the `db` service is running.

-   **Celery worker/beat not connecting to Redis:** Verify `REDIS_PASSWORD` and ensure the `redis` service is running.

### Restarting Services

```bash
# Restart a specific service
docker compose restart <service_name>

# Restart all services
docker compose restart

# Stop all services
docker compose stop

# Stop and remove all containers, networks, and volumes
docker compose down
```

## 📚 Next Steps

Once deployed, you can proceed with testing the API endpoints using the provided testing script or directly via the Swagger UI (`/docs`).

---
