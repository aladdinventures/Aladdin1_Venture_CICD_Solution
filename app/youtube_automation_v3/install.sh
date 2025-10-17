#!/bin/bash

# YouTube Automation System v3.0 - One-Click Installer for Ubuntu/Oracle Cloud
# Copyright (c) 2025 Saeed Alaediny. All rights reserved.

# --- Configuration ---
PROJECT_DIR="$(pwd)"
PROJECT_NAME="youtube_automation_v3"
ZIP_FILE="youtube_automation_v3.zip"

# --- Functions ---
log_info() {
    echo -e "\e[32mINFO: $1\e[0m"
}

log_warn() {
    echo -e "\e[33mWARN: $1\e[0m"
}

log_error() {
    echo -e "\e[31mERROR: $1\e[0m"
    exit 1
}

check_sudo() {
    sudo -v
    if [ $? -ne 0 ]; then
        log_error "Sudo privileges are required to run this script. Please ensure your user has sudo access."
    fi
}

install_docker() {
    log_info "Installing Docker..."
    sudo apt-get update || log_error "Failed to update apt packages."
    sudo apt-get install -y ca-certificates curl gnupg || log_error "Failed to install Docker prerequisites."
    
    sudo install -m 0755 -d /etc/apt/keyrings || log_error "Failed to create Docker keyrings directory."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg || log_error "Failed to download Docker GPG key."
    sudo chmod a+r /etc/apt/keyrings/docker.gpg || log_error "Failed to set permissions for Docker GPG key."
    
    echo \
      "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      \"$(. /etc/os-release && echo "$VERSION_CODENAME")\" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || log_error "Failed to add Docker repository."
    
    sudo apt-get update || log_error "Failed to update apt packages after adding Docker repo."
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || log_error "Failed to install Docker components."
    
    log_info "Adding current user to the docker group..."
    sudo usermod -aG docker "$USER" || log_error "Failed to add user to docker group."
    log_warn "Please log out and log back in (or reboot) for docker group changes to take effect."
    log_info "Restarting Docker service..."
    sudo systemctl restart docker || log_error "Failed to restart Docker service."
    log_info "Docker installed and configured."
}

configure_env() {
    log_info "Configuring environment variables..."
    if [ ! -f ".env.example" ]; then
        log_error ".env.example not found. Please ensure the project is extracted correctly."
    fi
    
    if [ ! -f ".env" ]; then
        cp .env.example .env || log_error "Failed to copy .env.example to .env."
        log_info "A .env file has been created from .env.example."
        log_warn "Please edit the .env file to configure your JWT_SECRET_KEY, SECRET_KEY, database passwords, and AI provider settings."
        log_warn "You can use 'nano .env' to edit the file. Press Ctrl+X, then Y, then Enter to save and exit."
        read -p "Press Enter to open .env for editing..." 
        nano .env
    else
        log_warn ".env file already exists. Skipping creation. Please ensure it's correctly configured."
    fi
}

build_and_start_services() {
    log_info "Building Docker images and starting services..."
    docker compose build || log_error "Docker Compose build failed."
    docker compose up -d || log_error "Docker Compose up failed."
    log_info "Docker services started successfully."
}

verify_services() {
    log_info "Verifying service status..."
    docker compose ps
    log_info "If all services show 'Up', the deployment was successful."
    log_info "You can access the API documentation at http://<your_server_ip>:8000/docs"
    log_info "Run the test script with: python3 test_api.py"
}

# --- Main Script Execution ---
log_info "Starting YouTube Automation System v3.0 One-Click Installer..."

check_sudo

# Check if Docker is already installed
if ! command -v docker &> /dev/null
then
    install_docker
else
    log_info "Docker is already installed. Skipping Docker installation."
    log_info "Ensuring current user is in docker group..."
    if ! groups "$USER" | grep -q "docker"; then
        sudo usermod -aG docker "$USER" || log_error "Failed to add user to docker group."
        log_warn "User added to docker group. Please log out and log back in (or reboot) for changes to take effect."
        log_info "Restarting Docker service..."
        sudo systemctl restart docker || log_error "Failed to restart Docker service."
    else
        log_info "User is already in the docker group."
    fi
fi

# Extract project if not already extracted
if [ ! -d "$PROJECT_NAME" ]; then
    log_info "Extracting project files..."
    if [ ! -f "$ZIP_FILE" ]; then
        log_error "Project zip file ($ZIP_FILE) not found in the current directory. Please ensure it's here."
    fi
    unzip "$ZIP_FILE" -d . || log_error "Failed to extract project zip file."
    log_info "Project extracted to $PROJECT_NAME."
fi

cd "$PROJECT_NAME" || log_error "Failed to change directory to $PROJECT_NAME."

configure_env
build_and_start_services
verify_services

log_info "Installation script finished. Please ensure you have configured your .env file and consider logging out/rebooting if prompted about docker group changes."

