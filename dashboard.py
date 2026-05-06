import streamlit as st
import json
import os
import glob
from datetime import datetime
from src.core.state import StateManager
from src.core.orchestrator import Orchestrator

# Page Configuration
st.set_page_config(
    page_title="Core Engine - Control Center",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .main-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .task-id {
        color: #58a6ff;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Managers
sm = StateManager()
orch = Orchestrator()

# Helper functions
def get_all_plans():
    plans = glob.glob(os.path.join("docs/brain", "plan_*.json"))
    plans.sort(reverse=True)
    return [os.path.basename(p) for p in plans]

# Sidebar
st.sidebar.title("🦾 Core Engine Orc")
st.sidebar.caption("v1.0 - Orchestrator Dashboard")

# Navigation
menu = st.sidebar.radio("Navigation", ["Dashboard", "Create New Project", "Project History"])

st.sidebar.markdown("---")
st.sidebar.info("Gunakan panel ini untuk mengontrol pengerjaan proyek berbasis Multi-Agent.")

# --- ROUTING ---

if menu == "Dashboard":
    st.title("🚀 Active Project")
    st.markdown("---")
    
    plan_data = sm.load_latest_plan()
    
    if plan_data:
        # Metrics
        completed = sum(1 for t in plan_data['tasks'] if t['status'] == 'completed')
        total = plan_data['total_tasks']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Project Name", plan_data['project_name'])
        c2.metric("Tasks Completed", f"{completed}/{total}")
        c3.metric("Status", "In Progress" if completed < total else "Completed")
        
        st.progress(completed/total)
        
        st.markdown("### 📋 Task Board")
        for task in plan_data['tasks']:
            with st.expander(f"Task {task['id']}: {task['title']} - [{task['status'].upper()}]"):
                col_left, col_right = st.columns([3, 1])
                
                with col_left:
                    st.write(task['description'])
                    st.caption(f"Agent Assigned: `{task['agent_type']}`")
                
                with col_right:
                    # Quick Status Update
                    status_options = ["pending", "in_progress", "completed"]
                    idx = status_options.index(task['status']) if task['status'] in status_options else 0
                    
                    new_status = st.selectbox("Update Status", status_options, index=idx, key=f"up_{task['id']}")
                    if new_status != task['status']:
                        sm.update_task_status(task['id'], new_status)
                        st.success(f"Status Updated!")
                        st.rerun()
    else:
        st.warning("Belum ada rencana aktif. Silakan buat proyek baru.")

elif menu == "Create New Project":
    st.title("➕ Create New Project")
    st.markdown("---")
    
    st.write("Masukkan deskripsi proyek yang ingin Anda kerjakan. Orchestrator akan merancang langkah-langkah teknisnya.")
    
    user_input = st.text_area("User Intent", placeholder="Contoh: Buat sistem manajemen gudang sederhana menggunakan Python...", height=150)
    
    if st.button("Generate Rencana Project"):
        if user_input:
            with st.spinner("AI sedang merancang rencana terbaik untuk Anda..."):
                try:
                    new_plan = orch.create_plan(user_input)
                    saved_path = sm.save_plan(new_plan)
                    st.success(f"Berhasil merancang: {new_plan.project_name}!")
                    st.balloons()
                    # Redirect ke Dashboard
                    st.info("Klik menu 'Dashboard' di sidebar untuk melihat rencana.")
                except Exception as e:
                    st.error(f"Gagal merancang: {e}")
        else:
            st.warning("Silakan masukkan deskripsi proyek terlebih dahulu.")

elif menu == "Project History":
    st.title("📂 Project History")
    st.markdown("---")
    
    all_plans = get_all_plans()
    if all_plans:
        selected_file = st.selectbox("Pilih Rencana Lama", all_plans)
        
        if selected_file:
            with open(os.path.join("docs/brain", selected_file), 'r') as f:
                history_data = json.load(f)
            
            st.header(f"Project: {history_data['project_name']}")
            st.json(history_data)
            
            if st.button("Jadikan ini Rencana Aktif"):
                # Copy to latest_plan.json
                with open(os.path.join("docs/brain", "latest_plan.json"), 'w') as f:
                    json.dump(history_data, f, indent=4)
                st.success("Berhasil mengembalikan rencana lama ke dashboard!")
    else:
        st.info("Belum ada riwayat proyek.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Core Engine Orc Dashboard v1.0")
