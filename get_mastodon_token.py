#!/usr/bin/env python3
"""
Mastodon Token Generator
Crea automaticamente un'app e ottiene il token
"""

from mastodon import Mastodon

print("🐘 Mastodon Token Generator")
print("="*50)

# Input
instance_url = input("\n🌐 Istanza Mastodon (es: fosstodon.org): ").strip()
if not instance_url.startswith('http'):
    instance_url = f"https://{instance_url}"

email = input("📧 Email: ").strip()
password = input("🔑 Password: ").strip()

print("\n🔄 Creando applicazione...")

# Step 1: Register app
Mastodon.create_app(
    'Tech Curator AI Bot',
    api_base_url=instance_url,
    to_file='mastodon_clientcred.secret'
)

print("✅ App registrata!")

# Step 2: Login and get token
print("🔐 Ottenendo access token...")

mastodon = Mastodon(
    client_id='mastodon_clientcred.secret',
    api_base_url=instance_url
)

access_token = mastodon.log_in(
    email,
    password,
    to_file='mastodon_usercred.secret'
)

print("\n🎉 SUCCESS!")
print("="*50)
print(f"\n🌐 Instance: {instance_url}")
print(f"🔑 Access Token:\n{access_token}")
print("\n💾 Add to .env:")
print(f"""
ENABLE_MASTODON=true
MASTODON_INSTANCE_URL={instance_url}
MASTODON_ACCESS_TOKEN={access_token}
""")
print("="*50)

# Cleanup
import os
try:
    os.remove('mastodon_clientcred.secret')
    os.remove('mastodon_usercred.secret')
except:
    pass

print("\n✅ Setup completo! Aggiungi le variabili a .env")
