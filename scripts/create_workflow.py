import os
import sys
import base64
import getpass

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests


def create_workflow():
    print("╔═══════════════════════════════════════════╗")
    print("║   Workflow Creator — Single Task         ║")
    print("╚═══════════════════════════════════════════╝")
    print()
    
    # Get token (hidden)
    token = getpass.getpass("GitHub Token (hidden): ").strip()
    if not token:
        print("No token provided")
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    api_url = 'https://api.github.com/repos/vahidmaghsoudi2/hbi/contents/.github/workflows/test.yml'
    
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
        echo "HBI Tests completed" >> $GITHUB_STEP_SUMMARY
"""
    
    content_base64 = base64.b64encode(workflow_content.encode('utf-8')).decode('utf-8')
    
    # Check if file exists
    print("\n[1/3] Checking if workflow exists...")
    check = requests.get(api_url, headers=headers, timeout=10)
    
    payload = {
        'message': 'ci: add GitHub Actions for automated testing',
        'content': content_base64,
        'branch': 'master'
    }
    
    if check.status_code == 200:
        payload['sha'] = check.json()['sha']
        print("   File exists, updating...")
    else:
        print("   Creating new file...")
    
    # Create/update
    print("\n[2/3] Sending to GitHub API...")
    response = requests.put(api_url, headers=headers, json=payload, timeout=15)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("\n[3/3] Verifying...")
        verify = requests.get(api_url, headers=headers, timeout=10)
        if verify.status_code == 200:
            print("   SHA: " + verify.json()['sha'][:7])
            print("\n╔═══════════════════════════════════════════╗")
            print("║   ✅ SUCCESS: Workflow Created           ║")
            print("╚═══════════════════════════════════════════╝")
            print("\nNext: Wait 1-2 min, then check:")
            print("   https://github.com/vahidmaghsoudi2/hbi/actions")
            return True
        else:
            print("   Verification failed")
            return False
    else:
        error = response.json().get('message', 'Unknown')
        print(f"   Error: {error}")
        
        if 'workflow' in error.lower():
            print("\n   Scope issue — use Web UI fallback")
        elif 'Bad credentials' in error:
            print("\n   Token invalid or revoked")
        elif 'rate limit' in error.lower():
            print("\n   Rate limit — wait and retry")
        
        return False


if __name__ == '__main__':
    success = create_workflow()
    sys.exit(0 if success else 1)
