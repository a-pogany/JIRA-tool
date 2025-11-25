#!/usr/bin/env python3
"""
Test Jira connection with current credentials
Run this to debug Jira authentication issues
"""

import os
from dotenv import load_dotenv
from jira_client import JiraClient
import requests

# Load environment variables
load_dotenv()

# Load credentials
jira_url = os.getenv('JIRA_URL', '')
jira_email = os.getenv('JIRA_EMAIL', '')
jira_api_token = os.getenv('JIRA_API_TOKEN', '')

print("=" * 60)
print("JIRA CONNECTION TEST")
print("=" * 60)

# Display configuration (masked token)
print(f"\nConfiguration:")
print(f"  JIRA_URL: {jira_url}")
print(f"  JIRA_EMAIL: {jira_email}")
print(f"  Token length: {len(jira_api_token)} characters")
print(f"  Token preview: {jira_api_token[:10]}...{jira_api_token[-10:]}")

# Check for common issues
print(f"\nPre-flight checks:")
issues = []

if not jira_url:
    issues.append("❌ JIRA_URL is empty")
else:
    print(f"✅ JIRA_URL is set")

if not jira_email:
    issues.append("❌ JIRA_EMAIL is empty")
else:
    print(f"✅ JIRA_EMAIL is set")

if not jira_api_token:
    issues.append("❌ JIRA_API_TOKEN is empty")
else:
    print(f"✅ JIRA_API_TOKEN is set")

# Check for quotes in token (common issue)
if jira_api_token.startswith('"') or jira_api_token.endswith('"'):
    issues.append("⚠️  Warning: Token appears to have quotes around it")
    print(f"⚠️  Warning: Token has quotes - this may cause authentication failure")
else:
    print(f"✅ Token format looks correct (no quotes)")

# Check URL format
if jira_url and not jira_url.startswith('http'):
    issues.append("❌ JIRA_URL should start with http:// or https://")
else:
    print(f"✅ URL format is correct")

if issues:
    print(f"\n⚠️  Found {len(issues)} issue(s) - please fix these first:")
    for issue in issues:
        print(f"  {issue}")
    print("\nExiting without testing connection.")
    exit(1)

# Test connection using JiraClient
print(f"\n" + "=" * 60)
print("Testing connection with JiraClient...")
print("=" * 60)

try:
    client = JiraClient(
        jira_url=jira_url,
        email=jira_email,
        api_token=jira_api_token
    )

    print(f"✅ JiraClient initialized")
    print(f"   URL: {client.jira_url}")

    print(f"\nCalling test_connection()...")
    if client.test_connection():
        print("✅ ✅ ✅ CONNECTION SUCCESSFUL! ✅ ✅ ✅")
        print("\nYour Jira credentials are working correctly.")
        print("If upload is still failing, check:")
        print("  - Backend server logs for detailed errors")
        print("  - Frontend browser console for request details")
        print("  - Markdown file path/permissions")
    else:
        print("❌ CONNECTION FAILED!")
        print("\nTrying to get more details...")

        # Manual request to get error details
        response = requests.get(
            f"{jira_url}/rest/api/3/myself",
            auth=(jira_email, jira_api_token),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            timeout=10
        )

        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(response.text[:500])

        if response.status_code == 401:
            print("\n❌ Authentication Error (401 Unauthorized)")
            print("\nPossible solutions:")
            print("  1. Generate a new API token at:")
            print("     https://id.atlassian.com/manage-profile/security/api-tokens")
            print("  2. Verify email matches your Atlassian account exactly")
            print("  3. Check token has no extra quotes or spaces in .env")
            print("  4. Ensure token hasn't expired")
        elif response.status_code == 403:
            print("\n❌ Permission Error (403 Forbidden)")
            print("\nYour token is valid but doesn't have required permissions.")
            print("Generate a new token with these permissions:")
            print("  - Read projects")
            print("  - Create issues")
            print("  - Edit issues")
        elif response.status_code == 404:
            print("\n❌ Not Found (404)")
            print("\nCheck your JIRA_URL - it may be incorrect.")
            print(f"Current URL: {jira_url}")
        else:
            print(f"\n❌ Unexpected error: {response.status_code}")

except Exception as e:
    print(f"❌ Error during connection test: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
