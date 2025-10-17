#!/usr/bin/env python3
import sys
import yaml
import os

CONFIG_PATH = "config/projects.yaml"

def main():
    if len(sys.argv) < 2:
        print("❌ [ERROR] Project name argument missing.")
        sys.exit(1)

    project_name = sys.argv[1]
    print(f"🔍 Validating project: {project_name}")

    if not os.path.exists(CONFIG_PATH):
        print(f"❌ [ERROR] Config file not found: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # The config structure is now a dictionary with a 'projects' key
    # We need to iterate through the list of projects to find the matching one
    found_project = None
    for project_entry in config.get('projects', []):
        if project_entry.get('name') == project_name:
            found_project = project_entry
            break

    if not found_project:
        print(f"❌ [ERROR] Project \'{project_name}\' not found in {CONFIG_PATH}")
        print("📌 Please add the project with proper configuration.")
        sys.exit(1)

    # check secrets
    # Assuming deploy_environments is a list of dictionaries within the found_project
    for env_config in found_project.get('deploy_environments', []):
        secret_name = env_config.get('render_api_key_secret_name')
        if secret_name and not os.getenv(secret_name):
            print(f"⚠️  [WARNING] Secret {secret_name} is not set in environment.")
            print("   This may cause deployment failure at later stages.")

    print(f"✅ [OK] Project \'{project_name}\' found in config.")
    sys.exit(0)

if __name__ == "__main__":
    main()
