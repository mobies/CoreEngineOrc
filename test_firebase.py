import os
from src.core.state import StateManager
from dotenv import load_dotenv

load_dotenv()

def test_firebase():
    print("--- Testing Firebase Cloud Sync ---")
    sm = StateManager()
    
    if not sm.firebase_enabled:
        print("[FAIL] Firebase tidak aktif. Cek .env dan keberadaan serviceAccountKey.json")
        return

    print("[OK] Firebase Client Berhasil Diinisialisasi.")
    
    # Test Listing
    print("[WAIT] Mencoba list projects dari Cloud...")
    projects = sm.list_all_projects()
    print(f"[OK] Ditemukan {len(projects)} proyek di Cloud/Local.")
    
    # Test Upload Dummy
    dummy_plan = {
        "project_name": "Firebase Connection Test",
        "total_tasks": 1,
        "tasks": [{"id": 1, "title": "Test Cloud Sync", "description": "Verify connection", "agent_type": "tester", "status": "pending"}]
    }
    print("[WAIT] Mencoba upload test plan ke Cloud...")
    path = sm.save_plan(dummy_plan)
    print(f"[SUCCESS] Test plan tersimpan di: {path}")

if __name__ == "__main__":
    test_firebase()
