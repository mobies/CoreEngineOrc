from src.core.orchestrator import Orchestrator
from src.core.state import StateManager

def test_full_cycle():
    print("=== Testing Core Engine: Planning & State Persistence ===")
    
    orch = Orchestrator()
    sm = StateManager()
    
    # 1. Buat Rencana
    user_request = "Buat modul enkripsi teks sederhana di Python."
    print(f"User Request: {user_request}")
    
    plan = orch.create_plan(user_request)
    print(f"Rencana berhasil dibuat: {plan.project_name}")
    
    # 2. Simpan Rencana ke Brain
    sm.save_plan(plan)
    
    # 3. Simulasi Update Status
    print("\nMengupdate status Tugas ID 1 menjadi 'completed'...")
    sm.update_task_status(1, "completed")
    
    # 4. Verifikasi Loading
    latest = sm.load_latest_plan()
    print("\n[VERIFIKASI DATA TERAKHIR]")
    print(f"Proyek: {latest['project_name']}")
    for t in latest['tasks']:
        print(f"- ID {t['id']}: {t['title']} | Status: {t['status']}")

if __name__ == "__main__":
    test_full_cycle()
