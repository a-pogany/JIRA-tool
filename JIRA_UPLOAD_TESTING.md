# JIRA Upload Testing Guide

## Overview
This document explains the JIRA upload flow and provides debugging strategies for credential issues.

## Upload Flow Architecture

### Frontend (React)
**File**: `ui/src/App.jsx`
**Function**: `handleUploadToJira()` (lines 82-131)

```javascript
const handleUploadToJira = async (filename) => {
  const payload = { filename }
  const response = await axios.post('/api/upload-to-jira', payload, {
    headers: { 'Content-Type': 'application/json' }
  })
}
```

**What it does**:
- Receives filename from ResultsPanel component
- Sends POST request to backend API endpoint `/api/upload-to-jira`
- Handles response and displays success/error messages

### Backend (Flask)
**File**: `app.py`
**Endpoint**: `/api/upload-to-jira` (lines 294-373)

**Upload Process**:
1. **Validation** (lines 319-321):
   ```python
   if not (config.jira_url and config.jira_email and config.jira_api_token):
       return jsonify({'error': 'Jira not configured...'}), 400
   ```

2. **File Parsing** (lines 328-335):
   - Reads markdown file
   - Parses into TicketStructure

3. **Jira Client Initialization** (lines 337-343):
   ```python
   jira_client = JiraClient(
       jira_url=config.jira_url,
       email=config.jira_email,
       api_token=config.jira_api_token
   )
   ```

4. **Connection Test** (lines 345-348):
   ```python
   if not jira_client.test_connection():
       return jsonify({'error': 'Failed to connect to Jira...'}), 400
   ```

5. **Upload** (lines 350-367):
   - Uploads epics, tasks, bugs, and stories
   - Returns results with created ticket keys

## Authentication Details

### Configuration Loading
**File**: `config.py`
**Lines**: 21-24

```python
jira_url: str = os.getenv('JIRA_URL', '')
jira_email: str = os.getenv('JIRA_EMAIL', '')
jira_api_token: str = os.getenv('JIRA_API_TOKEN', '')
jira_project: str = os.getenv('DEFAULT_PROJECT_KEY', '')
```

### Current .env Configuration
```
JIRA_URL=https://kaizendo-kft.atlassian.net/
JIRA_EMAIL=attila.pogany@gmail.com
JIRA_API_TOKEN="ATCTT3x..." (full token in .env)
```

### Jira Client Authentication
**File**: `jira_client.py`
**Lines**: 14-30

```python
def __init__(self, jira_url: str, email: str, api_token: str):
    self.jira_url = jira_url.rstrip('/')
    self.auth = (email, api_token)
    self.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
```

**Connection Test** (lines 32-48):
```python
def test_connection(self) -> bool:
    response = requests.get(
        f"{self.jira_url}/rest/api/3/myself",
        auth=self.auth,
        headers=self.headers,
        timeout=10
    )
    return response.status_code == 200
```

## Testing Strategies

### 1. Test Connection Directly

Create a test script `test_jira_connection.py`:

```python
#!/usr/bin/env python3
"""Test Jira connection with current credentials"""

import os
from dotenv import load_dotenv
from jira_client import JiraClient

load_dotenv()

# Load credentials
jira_url = os.getenv('JIRA_URL', '')
jira_email = os.getenv('JIRA_EMAIL', '')
jira_api_token = os.getenv('JIRA_API_TOKEN', '')

print(f"Testing connection to: {jira_url}")
print(f"Using email: {jira_email}")
print(f"Token length: {len(jira_api_token)}")

# Create client
client = JiraClient(
    jira_url=jira_url,
    email=jira_email,
    api_token=jira_api_token
)

# Test connection
print("\nTesting connection...")
if client.test_connection():
    print("✅ Connection successful!")
else:
    print("❌ Connection failed!")

    # Try to get more details
    import requests
    try:
        response = requests.get(
            f"{jira_url}/rest/api/3/myself",
            auth=(jira_email, jira_api_token),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
```

Run: `python3 test_jira_connection.py`

### 2. Check API Token Format

**Common Issues**:
- Token has quotes in .env: `JIRA_API_TOKEN="token"` vs `JIRA_API_TOKEN=token`
- Token has trailing/leading spaces
- Token expired or revoked

**Fix**: Ensure .env has clean token without extra quotes:
```bash
JIRA_API_TOKEN=ATCTT3xFfGN0W3TbM8MX3xkgPLXVN8FTZTrrTuPI7PH8YmN0KRvW8mvQFg-5vE0nC4CkRQ6Nlzay89p_xRZsSe_r1OiRyogNNboFhChbPo5o0ftaS-bI-dJZrF2crm9nIzNiNZjJSsSimIuY_DbulFOyWgpqD5wI4yoN55UYPaKEpEcuV3zlPL8=7E4712A3
```

### 3. Test with curl

Direct API test:
```bash
curl -X GET \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u "attila.pogany@gmail.com:ATCTT3x..." \
  "https://kaizendo-kft.atlassian.net/rest/api/3/myself"
```

Expected response if working:
```json
{
  "accountId": "...",
  "emailAddress": "attila.pogany@gmail.com",
  "displayName": "..."
}
```

### 4. Verify Token Permissions

Your API token needs these permissions:
- Read projects
- Create issues
- Edit issues
- Link issues

Check at: https://id.atlassian.com/manage-profile/security/api-tokens

### 5. Backend Server Logs

Check Flask backend logs for detailed error messages:
```bash
# Backend should be running with debug output
python3 app.py

# Look for these log messages:
[DEBUG] Upload to Jira - Raw data: {...}
[DEBUG] Upload to Jira - Extracted filename: ...
[DEBUG] Parsing markdown file: ...
[DEBUG] Initializing Jira client
[DEBUG] Testing Jira connection
```

### 6. Browser Console Debugging

In browser console (F12), check:
```javascript
// Check what's being sent
console.log('Payload:', payload)

// Check response
console.log('Response:', response.data)
console.log('Error:', err.response?.data)
```

## Common Issues & Solutions

### Issue: "Jira not configured"
**Cause**: Environment variables not loaded
**Solution**:
1. Verify .env file exists in project root
2. Restart Flask server to reload .env
3. Check config.py is loading dotenv correctly

### Issue: "Failed to connect to Jira"
**Cause**: Authentication failure at test_connection()
**Solution**:
1. Verify API token is valid and not expired
2. Check email matches Jira account
3. Test with curl (see above)
4. Generate new API token if needed

### Issue: "Invalid JSON data"
**Cause**: Frontend not sending correct payload
**Solution**:
1. Check browser console for payload structure
2. Verify filename is defined in frontend state
3. Check axios request headers

### Issue: Authentication 401
**Possible causes**:
1. Token has quotes wrapped around it in .env
2. Token expired (tokens last 365 days by default)
3. Email doesn't match Atlassian account
4. Token doesn't have required permissions

**Solution**:
```bash
# 1. Clean .env token (remove quotes)
JIRA_API_TOKEN=ATCTT3x...  # No quotes!

# 2. Generate new token
# Go to: https://id.atlassian.com/manage-profile/security/api-tokens
# Click "Create API token"
# Copy new token to .env

# 3. Restart Flask server
pkill -f "python.*app.py"
python3 app.py
```

## Quick Debugging Checklist

- [ ] .env file exists and has all three JIRA_ variables
- [ ] JIRA_API_TOKEN has no quotes around it
- [ ] Flask server restarted after .env changes
- [ ] Can access Jira URL in browser (not 404)
- [ ] Email matches Jira account exactly
- [ ] API token not expired (check Atlassian account)
- [ ] test_jira_connection.py script passes
- [ ] curl test returns 200 OK
- [ ] Browser console shows correct payload
- [ ] Flask logs show connection test running

## Next Steps for Your Case

Since you mentioned "the api key should be ok", here's what to verify:

1. **Check token format in .env**:
   ```bash
   grep JIRA_API_TOKEN .env
   # Should NOT have quotes: JIRA_API_TOKEN=token_here
   ```

2. **Test connection directly**:
   ```bash
   python3 test_jira_connection.py
   ```

3. **Check Flask logs** when uploading from UI - look for exact error message

4. **Try curl test** with your actual credentials to isolate if it's:
   - Backend code issue
   - Token issue
   - Network/firewall issue

Would you like me to create the test script for you to run?
