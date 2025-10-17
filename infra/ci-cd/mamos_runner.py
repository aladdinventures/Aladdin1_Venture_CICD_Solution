
import os
import yaml
import subprocess
import argparse
import requests
import datetime
import time
import signal

# Define constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(BASE_DIR, "..", "..")
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "projects.yaml")
REPORT_DIR = os.path.join(REPO_ROOT, "reports")
DETAILS_DIR = os.path.join(REPORT_DIR, "details")

# Ensure report directories exist
os.makedirs(DETAILS_DIR, exist_ok=True)

def load_config(config_path):
    """Loads the project configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_command(command, cwd, project_name, step_name):
    """Runs a shell command and captures its output and status."""
    print(f"\n--- Running {step_name} for {project_name} in {cwd} ---")
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{step_name} for {project_name} SUCCEEDED.")
        return True, process.stdout, process.stderr
    except subprocess.CalledProcessError as e:
        print(f"{step_name} for {project_name} FAILED.")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False, e.stdout, e.stderr
    except Exception as e:
        print(f"An unexpected error occurred during {step_name} for {project_name}: {e}")
        return False, "", str(e)

def generate_report(project_name, status, output, error, step_type="ci"):
    """Generates a detailed Markdown report for a project's CI/CD step."""
    report_file = os.path.join(DETAILS_DIR, f"{project_name}_report.md")
    with open(report_file, 'a', encoding='utf-8') as f:
        f.write(f"# {project_name} - {step_type.upper()} Report ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n")
        f.write(f"## Status: {'SUCCESS' if status else 'FAILURE'}\n\n")
        if output:
            f.write("### Output:\n")
            f.write(f"```bash\n{output}\n```\n\n")
        if error:
            f.write("### Error:\n")
            f.write(f"```bash\n{error}\n```\n\n")
        f.write("---\n\n")

def main(target_project=None, deploy_env=None):
    """Main function to run CI/CD pipeline for projects."""
    config = load_config(CONFIG_PATH)
    overall_status = True
    summary_report_content = []

    for project in config['projects']:
        project_name = project['name']
        project_path = os.path.join(REPO_ROOT, project['path'])

        if target_project and project_name != target_project:
            continue

        print(f"\n=====================================================")
        print(f"Starting CI/CD for project: {project_name}")
        print(f"=====================================================")

        build_status, build_output, build_error = True, "", ""
        test_status, test_output, test_error = True, "", ""
        start_status, start_output, start_error = True, "", ""
        deploy_status = True

        # 1. Build Step
        if 'build' in project:
            build_status, build_output, build_error = run_command(
                project['build'], project_path, project_name, "Build"
            )
            generate_report(project_name, build_status, build_output, build_error, "build")
            if not build_status:
                overall_status = False
                summary_report_content.append(f"- **{project_name}**: BUILD FAILED")
                continue

        # 2. Test Step
        if 'test' in project:
            test_status, test_output, test_error = run_command(
                project['test'], project_path, project_name, "Test"
            )
            generate_report(project_name, test_status, test_output, test_error, "test")
            if not test_status:
                overall_status = False
                summary_report_content.append(f"- **{project_name}**: TEST FAILED")
                continue

        # 3. Start/Health Check Step (Optional, for local verification)
        process = None
        if 'start' in project and 'health_check' in project:
            print(f"\n--- Starting {project_name} for health check ---")
            try:
                # Start the process in the background
                process = subprocess.Popen(
                    project['start'],
                    cwd=project_path,
                    shell=True,
                    preexec_fn=os.setsid, # To allow killing process group
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"Waiting for {project_name} to start...")
                
                health_check_url = project['health_check']['url']
                health_check_method = project['health_check'].get('method', 'GET')
                health_check_timeout = project['health_check'].get('timeout', 5)
                max_retries = 10 # Try for 10 * 5 = 50 seconds
                
                for i in range(max_retries):
                    try:
                        print(f"Attempt {i+1}/{max_retries}: Performing health check on {health_check_url} ({health_check_method})...")
                        response = requests.request(health_check_method, health_check_url, timeout=health_check_timeout)
                        response.raise_for_status()
                        start_status = True
                        start_output = f"Health check successful: {response.status_code} {response.text}"
                        print(f"Health check for {project_name} SUCCEEDED.")
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"Health check failed: {e}. Retrying in 5 seconds...")
                        time.sleep(5)
                else:
                    start_status = False
                    start_error = f"Health check failed after {max_retries} retries."
                    print(f"Health check for {project_name} FAILED after multiple retries.")

            except Exception as e:
                start_status = False
                start_error = f"Error starting or checking {project_name}: {e}"
                print(f"Error starting or checking {project_name}: {e}")
            finally:
                if process:
                    print(f"Stopping {project_name}...")
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=5)
                    stdout, stderr = process.communicate()
                    start_output += f"\nProcess Stdout:\n{stdout}"
                    start_error += f"\nProcess Stderr:\n{stderr}"
            generate_report(project_name, start_status, start_output, start_error, "start_check")
            if not start_status:
                overall_status = False
                summary_report_content.append(f"- **{project_name}**: HEALTH CHECK FAILED")
                continue

        # 4. Deployment Step (Render.com integration)
        if 'deploy' in project and deploy_env:
            for deploy_config in project['deploy']:
                if deploy_config['environment'] == deploy_env:
                    print(f"\n--- Deploying {project_name} to {deploy_env} on Render --- ")
                    try:
                        service_id = deploy_config['render_service_id']
                        api_key = os.environ.get('RENDER_API_KEY')
                        if not api_key:
                            raise ValueError("RENDER_API_KEY environment variable not set.")

                        headers = {
                            'Accept': 'application/json',
                            'Authorization': f'Bearer {api_key}'
                        }
                        deploy_url = f"https://api.render.com/v1/services/{service_id}/deploys"
                        
                        # Trigger deployment
                        response = requests.post(deploy_url, headers=headers)
                        response.raise_for_status()
                        deploy_data = response.json()
                        deploy_id = deploy_data.get('id')

                        if deploy_id:
                            print(f"Deployment triggered for {project_name}. Deploy ID: {deploy_id}")
                            status_url = f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}"
                            
                            # Poll for deployment status
                            current_status = ""
                            for _ in range(30): # Poll for up to 5 minutes (30 * 10 seconds)
                                time.sleep(10)
                                status_response = requests.get(status_url, headers=headers)
                                status_response.raise_for_status()
                                current_status = status_response.json().get('status')
                                print(f"Current deployment status: {current_status}")
                                if current_status in ['live', 'build_failed', 'deactivated', 'canceled']:
                                    break
                            
                            if current_status == 'live':
                                print(f"Deployment of {project_name} to {deploy_env} on Render SUCCESSFUL.")
                                summary_report_content.append(f"- **{project_name}**: Deployment to {deploy_env} SUCCESS")
                                generate_report(project_name, True, f'Render Deploy ID: {deploy_id}', '', 'deploy')
                            else:
                                print(f"Deployment of {project_name} to {deploy_env} on Render FAILED with status: {current_status}")
                                overall_status = False
                                summary_report_content.append(f"- **{project_name}**: Deployment to {deploy_env} FAILED")
                                generate_report(project_name, False, f'Render Deploy ID: {deploy_id}', f'Deployment status: {current_status}', 'deploy')
                        else:
                            print(f"Render deployment for {project_name} failed to return a deploy ID.")
                            overall_status = False
                            summary_report_content.append(f"- **{project_name}**: Deployment to {deploy_env} FAILED (No Deploy ID)")
                            generate_report(project_name, False, '', 'No Deploy ID from Render', 'deploy')
                    except requests.exceptions.RequestException as e:
                        print(f"Error triggering Render deployment for {project_name}: {e}")
                        overall_status = False
                        summary_report_content.append(f"- **{project_name}**: Deployment to {deploy_env} FAILED (Request Error)")
                        generate_report(project_name, False, '', f'Render API Request Error: {e}', 'deploy')
                    except Exception as e:
                        print(f"An unexpected error occurred during Render deployment for {project_name}: {e}")
                        overall_status = False
                        summary_report_content.append(f"- **{project_name}**: Deployment to {deploy_env} FAILED (Unexpected Error)")
                        generate_report(project_name, False, '', f'Unexpected Error: {e}', 'deploy')
                    break # Only deploy to the specified environment

        if build_status and test_status and start_status and deploy_status:
            summary_report_content.append(f"- **{project_name}**: SUCCESS")
        else:
            overall_status = False

    # Generate summary.md
    summary_path = os.path.join(REPORT_DIR, 'summary.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f'# MAMOS Test Summary - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write(f"## Overall Status: {'SUCCESS' if overall_status else 'FAILURE'}\n\n")
        f.write('### Project Statuses:\n')
        for line in summary_report_content:
            f.write(f'{line}\n')
        f.write('\n### Detailed Reports:\n')
        for project in config['projects']:
            f.write(f'- [{project["name"]}] Report](details/{project["name"]}_report.md)\n')

    print(f"\n--- MAMOS Run Complete ---")
    print(f"Overall Status: {'SUCCESS' if overall_status else 'FAILURE'}")
    print(f"Summary report: {summary_path}")
    print(f"Detailed reports in: {DETAILS_DIR}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAMOS CI/CD Runner')
    parser.add_argument('--project', type=str, help='Optional: Run CI/CD only for a specific project.')
    parser.add_argument('--deploy-env', type=str, help='Optional: Deploy to a specific environment (Test, Staging, Production).')
    args = parser.parse_args()
    main(args.project, args.deploy_env)

