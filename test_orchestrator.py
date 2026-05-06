from src.core.orchestrator import Orchestrator
from src.core.adapter import AIAdapter

def test_planning():
    print("=== Testing Core Engine Orchestrator ===")
    
    # Inisialisasi Orchestrator
    orch = Orchestrator()
    
    # Request simulasi dari User
    user_request = "Saya ingin membuat sistem login sederhana menggunakan Python yang menyimpan data di file CSV."
    
    print(f"Request: {user_request}\n")
    print("Orchestrator sedang merancang rencana...")
    
    try:
        # AI membuat rencana
        plan = orch.create_plan(user_request)
        
        print("\n[PLANNING RESULT]")
        print(f"Nama Proyek: {plan.project_name}")
        print(f"Total Tugas: {plan.total_tasks}")
        print("-" * 30)
        
        for task in plan.tasks:
            dep = f" (Menunggu tugas {task.dependencies})" if task.dependencies else ""
            print(f"ID {task.id}: {task.title} [{task.agent_type}]{dep}")
            print(f"Deskripsi: {task.description}\n")
            
        print("[SUCCESS] Orchestrator berhasil membuat rencana teknis!")
        
    except Exception as e:
        print(f"[ERROR] Gagal merancang rencana: {e}")

if __name__ == "__main__":
    test_planning()
