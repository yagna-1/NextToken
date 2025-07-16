#!/usr/bin/env python3
"""
Demo script for NexToken API
"""

import requests
import json
import time
from datetime import datetime


def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)


def demo_nextoken_api():
    """Demonstrate NexToken API functionality"""
    base_url = "http://localhost:8000"
    
    print_separator("NexToken API Demo")
    
    # Test health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Status: {health_data['status']}")
            print(f"📦 Version: {health_data['version']}")
            print(f"🕒 Timestamp: {health_data['timestamp']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running with:")
        print("   uvicorn nextoken.main:app --reload")
        return
    
    # Test token issuance
    print("\n2. Token Issuance")
    issue_data = {
        "user_id": "demo_user_123",
        "email": "demo@example.com",
        "expires_in": 3600,
        "custom_claims": {
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/issue", json=issue_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token issued successfully!")
            print(f"🆔 Token ID: {token_data['token_id']}")
            print(f"⏰ Expires at: {token_data['expires_at']}")
            print(f"🔑 Token (first 50 chars): {token_data['token'][:50]}...")
            
            token = token_data['token']
        else:
            print(f"❌ Token issuance failed: {response.status_code}")
            print(f"Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error issuing token: {e}")
        return
    
    # Test token verification
    print("\n3. Token Verification")
    verify_data = {"token": token}
    
    try:
        response = requests.post(f"{base_url}/api/v1/verify", json=verify_data)
        if response.status_code == 200:
            verify_result = response.json()
            if verify_result['valid']:
                print("✅ Token is valid!")
                print(f"👤 User ID: {verify_result['user_id']}")
                print(f"📧 Email: {verify_result['email']}")
                print(f"🎭 Custom claims: {verify_result['custom_claims']}")
                print(f"⏰ Expires at: {verify_result['expires_at']}")
                print(f"🕒 Issued at: {verify_result['issued_at']}")
            else:
                print(f"❌ Token is invalid: {verify_result['error']}")
        else:
            print(f"❌ Token verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying token: {e}")
    
    # Test token revocation
    print("\n4. Token Revocation")
    revoke_data = {"token": token}
    
    try:
        response = requests.post(f"{base_url}/api/v1/revoke", json=revoke_data)
        if response.status_code == 200:
            revoke_result = response.json()
            if revoke_result['success']:
                print("✅ Token revoked successfully!")
                print(f"💬 Message: {revoke_result['message']}")
            else:
                print(f"❌ Token revocation failed: {revoke_result['message']}")
        else:
            print(f"❌ Token revocation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error revoking token: {e}")
    
    # Test verification of revoked token
    print("\n5. Verify Revoked Token")
    try:
        response = requests.post(f"{base_url}/api/v1/verify", json=verify_data)
        if response.status_code == 200:
            verify_result = response.json()
            if not verify_result['valid']:
                print("✅ Correctly detected revoked token!")
                print(f"❌ Error: {verify_result['error']}")
            else:
                print("❌ Failed to detect revoked token!")
        else:
            print(f"❌ Verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying revoked token: {e}")
    
    # Test statistics
    print("\n6. Token Statistics")
    try:
        response = requests.get(f"{base_url}/api/v1/stats")
        if response.status_code == 200:
            stats = response.json()
            print("📊 Token Statistics:")
            print(f"   Active tokens: {stats['active_tokens']}")
            print(f"   Revoked tokens: {stats['revoked_tokens']}")
            print(f"   Total tokens: {stats['total_tokens']}")
            print(f"   Timestamp: {stats['timestamp']}")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    # Test API info
    print("\n7. API Information")
    try:
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            info = response.json()
            print("ℹ️  API Information:")
            print(f"   Name: {info['name']}")
            print(f"   Version: {info['version']}")
            print(f"   Description: {info['description']}")
            print("   Features:")
            for feature in info['features']:
                print(f"     • {feature}")
        else:
            print(f"❌ Failed to get API info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting API info: {e}")
    
    print_separator("Demo Complete")
    print("🎉 NexToken demo completed successfully!")
    print("\n📚 Next steps:")
    print("   • Check out the API documentation at: http://localhost:8000/docs")
    print("   • Explore the interactive Swagger UI")
    print("   • Try different token configurations")
    print("   • Test with your own applications!")


if __name__ == "__main__":
    demo_nextoken_api() 