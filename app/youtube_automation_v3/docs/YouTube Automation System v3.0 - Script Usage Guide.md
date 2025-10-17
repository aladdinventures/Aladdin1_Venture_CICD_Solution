# YouTube Automation System v3.0 - `install.sh` Script Usage Guide

**Copyright © 2025 Saeed Alaediny. All rights reserved.**

This guide provides step-by-step instructions on how to use the `install.sh` script to automatically deploy the YouTube Automation System v3.0 on an Ubuntu server, particularly on Oracle Cloud.

## 🎯 Purpose of `install.sh`

The `install.sh` script automates the entire deployment process, including:
-   Checking for `sudo` privileges.
-   Installing Docker and Docker Compose (if not already present).
-   Adding the current user to the `docker` group.
-   Extracting the project files from `youtube_automation_v3.zip`.
-   Guiding you through the `.env` file configuration.
-   Building Docker images and starting all services (web, db, redis, celery_worker, celery_beat).
-   Verifying the status of the deployed services.

## 🚀 Prerequisites

Before running the script, ensure you have:

1.  **An Ubuntu Server:** Preferably on Oracle Cloud, with SSH access.
2.  **`sudo` Privileges:** Your user account must have `sudo` access.
3.  **Project Package:** The `youtube_automation_v3.zip` file (provided previously) must be available.
4.  **`install.sh` Script:** The `install.sh` script itself (provided previously) must be available.

## 📦 Preparation Steps

1.  **Upload Files to Your Server:**
    Transfer both `youtube_automation_v3.zip` and `install.sh` to your home directory on the Ubuntu server. You can use `scp` or any other secure file transfer method.

    ```bash
    # Example using scp from your local machine
    scp /path/to/local/youtube_automation_v3.zip ubuntu@your_server_ip:~/
    scp /path/to/local/install.sh ubuntu@your_server_ip:~/
    ```

2.  **Connect to Your Server:**
    SSH into your Oracle Cloud Ubuntu instance.

    ```bash
    ssh ubuntu@your_server_ip
    ```

## ⚙️ Running the `install.sh` Script

Once connected to your server and with the files uploaded, follow these steps:

1.  **Make the Script Executable:**
    You need to give execute permissions to the `install.sh` script.

    ```bash
    chmod +x install.sh
    ```

2.  **Execute the Script:**
    Run the script from your home directory.

    ```bash
    ./install.sh
    ```

3.  **Follow On-Screen Prompts:**
    The script will guide you through the installation process:
    -   It will first check for `sudo` access.
    -   It will install Docker and Docker Compose if they are not found.
    -   It will add your user to the `docker` group. **Important:** If this happens, the script will warn you to **log out and log back in (or reboot)** for the changes to take effect. You might need to do this before proceeding with Docker Compose commands.
    -   It will extract the `youtube_automation_v3.zip` into a new directory named `youtube_automation_v3`.
    -   It will then prompt you to **edit the `.env` file**. This is a crucial step where you must configure sensitive variables like `JWT_SECRET_KEY`, `SECRET_KEY`, database passwords, and AI provider settings. The script will open `nano .env` for you. After editing, save and exit (`Ctrl+X`, then `Y`, then `Enter`).

4.  **Docker Compose Build and Up:**
    After you've configured the `.env` file, the script will automatically proceed to build the Docker images and start all services in detached mode (`docker compose build` and `docker compose up -d`).

5.  **Verify Services:**
    Finally, the script will display the status of your Docker containers (`docker compose ps`). You should see all services (`web`, `db`, `redis`, `celery_worker`, `celery_beat`) in an `Up` state.

## ✅ Post-Installation

-   **Access the API:** The FastAPI application will be accessible on port `8000` of your server.
    -   **Health Check:** `http://your_server_ip:8000/health`
    -   **API Documentation (Swagger UI):** `http://your_server_ip:8000/docs`
-   **Run Tests:** You can run the provided API testing script (`test_api.py`) from within the `youtube_automation_v3` directory to validate the endpoints.
    ```bash
    cd youtube_automation_v3
    python3 test_api.py
    ```

## 🐛 Troubleshooting

-   **`docker` command not found after installation:** This usually means you need to log out and log back in (or reboot your server) for the `docker` group membership to take effect.
-   **Containers not starting:** Check the logs of individual services using `docker compose logs <service_name>` (e.g., `docker compose logs web`).
-   **`.env` configuration issues:** Double-check your `.env` file for correct values, especially passwords and API keys.

If you encounter any persistent issues, please provide the full output of the `install.sh` script and any relevant Docker Compose logs.
