#!/usr/bin/env python3
"""
HBI GitHub Direct Connector v2
Fixed: URL encoding, branch detection, scope validation
"""

import os
import sys
import base64
import getpass
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests


def main():
    print("╔═══════════════════════════════════════════╗")
    print("║   HBI GitHub Connector v2                ║")
    print("╚═══════════════════════════════════════════╝")
    print()
    
    # Get token securely (hidden input)
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        token = getpass.getpass("Enter your GitHub Token (hidden): ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repo_owner = 'vahidmaghsoudi2'
    repo_name = 'hbi'
    api_base = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
    
    # Step 1: Test connection and get default branch
    print("\n[1/5] Testing connection...")
    try:
        response = requests.get(f'{api_base}', headers=headers, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            default_branch = repo_data.get('default_branch', 'master')
            print(f"✅ Connected to: {repo_owner}/{repo_name}")
            print(f"   Default branch: {default_branch}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"   Error: {response.json().get('message', 'Unknown error')}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Step 2: Check token scopes
    print("\n[2/5] Checking token scopes...")
    try:
        response = requests.get(f'https://api.github.com/user', headers=headers, timeout=10)
        scopes = response.headers.get('X-OAuth-Scopes', 'none')
        print(f"   Token scopes: {scopes}")
        
        if 'workflow' not in scopes:
            print("⚠️  WARNING: Token does NOT have 'workflow' scope!")
            print("   Workflow files cannot be created without this scope.")
            print("   Please create a new token with 'workflow' scope.")
            print("   Continuing with other checks...")
    except Exception as e:
        print(f"⚠️  Could not check scopes: {e}")
    
    # Step 3: Get latest commit
    print("\n[3/5] Getting latest commit...")
    try:
        response = requests.get(f'{api_base}/commits?per_page=3', headers=headers, timeout=10)
        if response.status_code == 200:
            commits = response.json()
            for c in commits[:3]:
                print(f"   {c['sha'][:7]} | {c['commit']['message'].split(chr(10))[0][:60]}")
        else:
            print(f"❌ Failed to get commits: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Create workflow file (with proper URL encoding)
    print("\n[4/5] Creating workflow file...")
    
    workflow_content = """name: HBI Tests

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
    
    - name: Test Summary
      if: always()
      run: |
        echo "## Test Results" >> $GITHUB_STEP_SUMMARY
        echo "Tests completed" >> $GITHUB_STEP_SUMMARY
"""
    
    content_bytes = workflow_content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # URL-encode the path
    workflow_path = quote('.github/workflows/test.yml', safe='')
    
    try:
        # First check if file exists
        check_response = requests.get(
            f'{api_base}/contents/.github/workflows/test.yml',
            headers=headers,
            timeout=10
        )
        
        payload = {
            'message': 'ci: add GitHub Actions for automated testing',
            'content': content_base64,
            'branch': default_branch
        }
        
        # If file exists, include SHA
        if check_response.status_code == 200:
            existing_sha = check_response.json()['sha']
            payload['sha'] = existing_sha
            print("   File exists, updating...")
        else:
            print("   Creating new file...")
        
        create_response = requests.put(
            f'{api_base}/contents/.github/workflows/test.yml',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if create_response.status_code in [200, 201]:
            print("✅ Workflow file created/updated successfully!")
        else:
            error_msg = create_response.json().get('message', 'Unknown error')
            print(f"❌ Failed: {create_response.status_code}")
            print(f"   Error: {error_msg}")
            
            if 'workflow' in error_msg.lower() or create_response.status_code == 404:
                print("\n⚠️  This is likely a scope issue.")
                print("   Your token needs 'workflow' scope to create workflow files.")
                print("   Solution:")
                print("   1. Go to: https://github.com/settings/tokens")
                print("   2. Create NEW token with scopes: repo + workflow")
                print("   3. Run this script again with the new token")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Check Actions
    print("\n[5/5] Checking GitHub Actions...")
    try:
        response = requests.get(
            f'{api_base}/actions/runs?per_page=1',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            runs = response.json()
            if runs['total_count'] > 0:
                latest_run = runs['workflow_runs'][0]
                print(f"✅ Actions found: {runs['total_count']} total")
                print(f"   Latest: {latest_run['name']}")
                print(f"   Status: {latest_run['status']} / {latest_run.get('conclusion', 'pending')}")
                print(f"   URL: {latest_run['html_url']}")
            else:
                print("⚠️  No Actions runs yet (will start after workflow file is created)")
        else:
            print(f"⚠️  Could not check Actions: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not check Actions: {e}")
    
    # Summary
    print("\n╔═══════════════════════════════════════════╗")
    print("║   Connection Summary                      ║")
    print("╠═══════════════════════════════════════════╣")
    print(f"║ Repo: {repo_owner}/{repo_name}")
    print(f"║ Branch: {default_branch}")
    print(f"║ URL: https://github.com/{repo_owner}/{repo_name}")
    print(f"║ Actions: https://github.com/{repo_owner}/{repo_name}/actions")
    print("╚═══════════════════════════════════════════╝")


if __name__ == '__main__':
    main()
