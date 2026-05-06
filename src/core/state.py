import json
import os
from datetime import datetime
from typing import Optional, List
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv

load_dotenv()

class StateManager:
    """
    Manages the persistence of project plans and task statuses with Firebase Cloud Sync.
    """
    
    def __init__(self, base_path: str = "docs/brain"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
        self.firebase_enabled = False
        self._init_firebase()

    def _init_firebase(self):
        # Try to get from Streamlit Secrets first (for Cloud Deployment)
        try:
            import streamlit as st
            if "firebase" in st.secrets:
                secret_dict = dict(st.secrets["firebase"])
                bucket_name = st.secrets.get("FIREBASE_STORAGE_BUCKET")
                
                if not firebase_admin._apps:
                    cred = credentials.Certificate(secret_dict)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': bucket_name
                    })
                self.bucket = storage.bucket()
                self.firebase_enabled = True
                return
        except:
            pass

        # Fallback to Local (.env and file)
        service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
        
        if service_account and os.path.exists(service_account) and bucket_name:
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(service_account)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': bucket_name
                    })
                self.bucket = storage.bucket()
                self.firebase_enabled = True
            except Exception as e:
                print(f"[WARNING] Gagal inisialisasi Firebase: {e}")

    def save_plan(self, plan_data_obj):
        """
        Saves a ProjectPlan locally and syncs to Firebase Storage.
        """
        if hasattr(plan_data_obj, 'dict'):
            plan_data = plan_data_obj.dict()
        else:
            plan_data = plan_data_obj

        filename = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        local_path = os.path.join(self.base_path, filename)
        latest_path = os.path.join(self.base_path, "latest_plan.json")
        
        # Ensure status exists
        for task in plan_data.get('tasks', []):
            if 'status' not in task: task['status'] = 'pending'
        
        # Save Locally
        with open(local_path, 'w') as f:
            json.dump(plan_data, f, indent=4)
        with open(latest_path, 'w') as f:
            json.dump(plan_data, f, indent=4)
            
        # Sync to Firebase
        if self.firebase_enabled:
            try:
                blob = self.bucket.blob(f"projects/{filename}")
                blob.upload_from_filename(local_path)
                
                latest_blob = self.bucket.blob("projects/latest_plan.json")
                latest_blob.upload_from_filename(latest_path)
                print(f"[SUCCESS] Cloud Sync Berhasil: {filename}")
            except Exception as e:
                print(f"[ERROR] Cloud Sync Gagal: {e}")
        
        print(f"[SUCCESS] Rencana disimpan lokal: {local_path}")
        return local_path

    def load_latest_plan(self) -> Optional[dict]:
        """
        Loads the latest plan (from Firebase if enabled, else local).
        """
        latest_path = os.path.join(self.base_path, "latest_plan.json")
        
        if self.firebase_enabled:
            try:
                blob = self.bucket.blob("projects/latest_plan.json")
                if blob.exists():
                    blob.download_to_filename(latest_path)
                    print("[INFO] Latest plan disinkronkan dari Cloud.")
            except Exception as e:
                print(f"[WARNING] Gagal sync dari Cloud, menggunakan local: {e}")

        if os.path.exists(latest_path):
            with open(latest_path, 'r') as f:
                return json.load(f)
        return None

    def update_task_status(self, task_id: int, status: str):
        """
        Updates task status and triggers re-sync.
        """
        plan_data = self.load_latest_plan()
        if not plan_data: return

        for task in plan_data['tasks']:
            if task['id'] == task_id:
                task['status'] = status
                break
        
        # Re-save which triggers sync
        self.save_plan(plan_data)

    def list_all_projects(self) -> List[str]:
        """
        Lists all projects from Cloud if enabled, else local.
        """
        if self.firebase_enabled:
            try:
                blobs = self.bucket.list_blobs(prefix="projects/plan_")
                cloud_files = [os.path.basename(b.name) for b in blobs]
                # Sync them to local for visibility
                for b_name in cloud_files:
                    lp = os.path.join(self.base_path, b_name)
                    if not os.path.exists(lp):
                        self.bucket.blob(f"projects/{b_name}").download_to_filename(lp)
                return cloud_files
            except Exception as e:
                print(f"[ERROR] Gagal list cloud projects: {e}")
        
        import glob
        plans = glob.glob(os.path.join(self.base_path, "plan_*.json"))
        return [os.path.basename(p) for p in plans]

    def delete_project(self, filename: str):
        """
        Deletes a project locally and from Cloud.
        """
        local_path = os.path.join(self.base_path, filename)
        if os.path.exists(local_path):
            os.remove(local_path)
            print(f"[INFO] File lokal {filename} dihapus.")

        if self.firebase_enabled:
            try:
                blob = self.bucket.blob(f"projects/{filename}")
                if blob.exists():
                    blob.delete()
                    print(f"[SUCCESS] Cloud file {filename} dihapus.")
            except Exception as e:
                print(f"[ERROR] Gagal hapus cloud file: {e}")
