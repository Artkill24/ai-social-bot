#!/usr/bin/env python3
"""
LinkedIn OAuth Helper - Get Access Token
IMPORTANT: Add your credentials here, but DON'T commit them!
"""

import requests
from urllib.parse import urlencode
import webbrowser

# TODO: Add your credentials here (from LinkedIn Developer Console)
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://localhost:8080/callback"

def get_auth_url():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'w_member_social'
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    print("🔐 LinkedIn OAuth Flow")
    print("="*50)
    print("\n1. Open this URL in browser:")
    print(f"\n{auth_url}\n")
    print("2. Authorize the app")
    print("3. You'll be redirected to localhost (error is normal)")
    print("4. Copy the 'code' from URL (after ?code=...)")
    print("\n" + "="*50)
    
    webbrowser.open(auth_url)
    return input("\n📋 Paste CODE here: ").strip()

def get_access_token(code):
    print("\n🔄 Exchanging code for token...")
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data=data
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        
        print("\n✅ SUCCESS!")
        print("="*50)
        print(f"\nAccess Token:\n{access_token}")
        print("\n⏰ Expires in:", token_data.get('expires_in', 'Unknown'), "seconds")
        print("\n💾 Add to .env:")
        print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")
        print("\n" + "="*50)
        
        return access_token
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None

def get_user_id(access_token):
    print("\n👤 Getting User ID...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        'https://api.linkedin.com/v2/userinfo',
        headers=headers
    )
    
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get('sub', '')
        
        print("\n✅ User ID obtained!")
        print("="*50)
        print(f"\nUser ID: {user_id}")
        print("\n💾 Add to .env:")
        print(f"\nLINKEDIN_USER_ID={user_id}")
        print("\n" + "="*50)
        
        return user_id
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("\n⚠️  Before continuing:")
    print("1. Created LinkedIn app?")
    print("2. Added CLIENT_ID and CLIENT_SECRET to this file?")
    print("3. Added redirect URI: http://localhost:8080/callback")
    input("\nPress Enter to continue...")
    
    code = get_auth_url()
    
    if code:
        access_token = get_access_token(code)
        
        if access_token:
            user_id = get_user_id(access_token)
            
            if user_id:
                print("\n🎉 SETUP COMPLETE!")
                print("\nAdd to .env:")
                print(f"""
ENABLE_LINKEDIN=true
LINKEDIN_ACCESS_TOKEN={access_token}
LINKEDIN_USER_ID={user_id}
""")
