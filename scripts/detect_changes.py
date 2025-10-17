import os
import subprocess
import json

def get_changed_files():
    # Get changes between current branch and its merge base with the target branch (e.g., main or develop)
    # For PRs, compare against the base branch (e.g., main or develop).
    # For pushes, compare against the previous commit.
    try:
        # Determine the base for comparison
        if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
            base_ref = os.environ.get('GITHUB_BASE_REF')
            if not base_ref:
                print("GITHUB_BASE_REF not found for pull_request event.")
                return []
            # Fetch the base branch to ensure it's available for comparison
            subprocess.run(['git', 'fetch', 'origin', base_ref], check=True)
            compare_ref = f'origin/{base_ref}'
        else:
            # For push events, compare with the previous commit
            compare_ref = 'HEAD~1'

        command = ['git', 'diff', '--name-only', compare_ref, 'HEAD']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
        print(f"Stderr: {e.stderr}")
        return []

def detect_affected_projects(changed_files):
    affected_projects = set()
    project_map = {}

    # Define prefixes for apps and packages
    app_prefix = 'apps/'
    package_prefix = 'packages/'

    # Get a list of all existing apps and packages
    all_apps = [name for name in os.listdir(app_prefix) if os.path.isdir(os.path.join(app_prefix, name))]
    all_packages = [name for name in os.listdir(package_prefix) if os.path.isdir(os.path.join(package_prefix, name))]

    for f in changed_files:
        if f.startswith(app_prefix):
            parts = f[len(app_prefix):].split(os.sep)
            if len(parts) > 0:
                project_name = parts[0]
                if project_name in all_apps:
                    affected_projects.add(f'{app_prefix}{project_name}')
        elif f.startswith(package_prefix):
            parts = f[len(package_prefix):].split(os.sep)
            if len(parts) > 0:
                project_name = parts[0]
                if project_name in all_packages:
                    affected_projects.add(f'{package_prefix}{project_name}')
        else:
            # If a change is outside of apps/ or packages/, assume all projects are affected
            # or handle specific cases (e.g., change in shared/core might affect all)
            # For now, let's assume changes outside these directories trigger all CI.
            # A more sophisticated approach would map shared changes to dependent projects.
            affected_projects.add('all') # Special marker to indicate all projects
            break

    if 'all' in affected_projects or not affected_projects:
        # If 'all' was added or no specific projects were affected (e.g., only workflow file changed),
        # then include all known apps and packages.
        # This ensures CI runs for everything if a core change happens or if the detection is too narrow.
        if 'all' in affected_projects:
            print("Change detected outside of specific app/package directories or no specific projects affected. Running CI for all projects.")
        else:
            print("No specific app/package changes detected. Running CI for all projects as a fallback.")
        return [f'{app_prefix}{app}' for app in all_apps] + \
               [f'{package_prefix}{pkg}' for pkg in all_packages]

    return list(affected_projects)

if __name__ == '__main__':
    # Ensure we are in the root of the repository
    os.chdir(os.environ.get('GITHUB_WORKSPACE', '.'))

    changed_files = get_changed_files()
    print(f"Changed files: {changed_files}")

    affected = detect_affected_projects(changed_files)
    print(f"Affected projects: {affected}")

    # Output affected projects as a JSON array for GitHub Actions
    print(f"::set-output name=affected_projects::{json.dumps(affected)}")

