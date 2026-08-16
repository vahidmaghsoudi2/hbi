import os
import sys
import base64
import requests

token = os.environ.get('GITHUB_TOKEN', '').strip()

print("=== Token Validation ===")
print(f"Token length: {len(token)}")
print(f"Token prefix: {token[:8]}..." if token else "Token: EMPTY")

# Validate format
if not token:
    print("ERROR: Token is empty")
    sys.exit(1)

if token.startswith('ghp_'):
    print("Format: Classic token (ghp_) - OK")
elif token.startswith('github_pat_'):
    print("Format: Fine-grained token - may have issues")
else:
    print(f"WARNING: Unknown format. Expected ghp_ or github_pat_")

# Test token with simple API call
print("\n=== Testing Token ===")
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

r = requests.get('https://api.github.com/user', headers=headers, timeout=10)
print(f"GET /user status: {r.status_code}")

if r.status_code == 200:
    user = r.json()
    print(f"Authenticated as: {user['login']}")
    print("Token is VALID")
else:
    print(f"Token test FAILED: {r.json().get('message', 'Unknown error')}")
    sys.exit(1)

# Now create workflow
print("\n=== Creating Workflow ===")
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

check = requests.get(api_url, headers=headers, timeout=10)
payload = {
    'message': 'ci: add GitHub Actions for automated testing',
    'content': content_base64,
    'branch': 'master'
}

if check.status_code == 200:
    payload['sha'] = check.json()['sha']
    print("File exists, updating...")
else:
    print("Creating new file...")

response = requests.put(api_url, headers=headers, json=payload, timeout=15)
print(f"PUT status: {response.status_code}")

if response.status_code in [200, 201]:
    print("\n=== SUCCESS ===")
    print("Workflow created!")
    print("Check: https://github.com/vahidmaghsoudi2/hbi/actions")
else:
    error = response.json().get('message', 'Unknown')
    print(f"\n=== FAILED ===")
    print(f"Error: {error}")
    if 'workflow' in error.lower():
        print("Hint: Token needs 'workflow' scope")
