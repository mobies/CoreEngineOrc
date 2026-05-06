import json
import os
from datetime import datetime
from typing import Optional
from .orchestrator import ProjectPlan, Task

class StateManager:
    """
    Manages the persistence of project plans and task statuses.
    """
    
    def __init__(self, base_path: str = "docs/brain"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def save_plan(self, plan: ProjectPlan):
        """
        Saves a ProjectPlan to a JSON file.
        """
        filename = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.base_path, filename)
        
        # Add 'status' to each task if not present
        plan_data = plan.dict()
        for task in plan_data['tasks']:
            if 'status' not in task:
                task['status'] = 'pending'
        
        with open(filepath, 'w') as f:
            json.dump(plan_data, f, indent=4)
        
        # Also save as latest_plan.json for easy access
        latest_path = os.path.join(self.base_path, "latest_plan.json")
        with open(latest_path, 'w') as f:
            json.dump(plan_data, f, indent=4)
            
        print(f"[SUCCESS] Rencana proyek disimpan di: {filepath}")
        return filepath

    def load_latest_plan(self) -> Optional[dict]:
        """
        Loads the latest project plan.
        """
        latest_path = os.path.join(self.base_path, "latest_plan.json")
        if os.path.exists(latest_path):
            with open(latest_path, 'r') as f:
                return json.load(f)
        return None

    def update_task_status(self, task_id: int, status: str):
        """
        Updates the status of a specific task in the latest plan.
        """
        plan_data = self.load_latest_plan()
        if not plan_data:
            print("[ERROR] Tidak ada rencana aktif yang bisa diupdate.")
            return

        for task in plan_data['tasks']:
            if task['id'] == task_id:
                task['status'] = status
                break
        
        latest_path = os.path.join(self.base_path, "latest_plan.json")
        with open(latest_path, 'w') as f:
            json.dump(plan_data, f, indent=4)
        
        print(f"[SUCCESS] Status Tugas ID {task_id} diupdate menjadi: {status}")

if __name__ == "__main__":
    # Quick test
    sm = StateManager()
    print("State Manager initialized.")
