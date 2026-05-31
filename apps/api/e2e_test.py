import httpx
import json

API_URL = "http://localhost:8000/api/v1"

def run_test():
    print("========================================")
    print("AxonBridge Phase 1: End-to-End Test")
    print("========================================\n")
    
    with httpx.Client() as client:
        # 1. Login
        print("[1/3] Authenticating as Admin...")
        res = client.post(f"{API_URL}/auth/login", json={
            "email": "admin@axonbridge.io",
            "password": "AxonBridge2026!"
        })
        if res.status_code != 200:
            print(f"❌ Login failed! Status: {res.status_code}")
            print(res.text)
            return
            
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✅ Successfully logged in and received JWT\n")
        
        # 2. Fetch Profile
        print("[2/3] Fetching User Profile...")
        res = client.get(f"{API_URL}/users/me", headers=headers)
        if res.status_code != 200:
            print("❌ Profile fetch failed!")
            return
            
        profile = res.json()
        print(f"  ✅ Profile fetched: {profile['full_name']} ({profile['email']})\n")
        
        print("\n========================================")
        print("🎉 Phase 1 E2E Test Completed Successfully!")
        print("========================================\n")

if __name__ == "__main__":
    run_test()
