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
    .folder-box {
        background-color: #21262d;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        color: #8b949e;
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
st.sidebar.caption("v1.1 - Industrial Dashboard")

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
        
        # Tech Stack & Cost Insight
        col_tech, col_cost = st.columns(2)
        with col_tech:
            with st.container(border=True):
                st.markdown("#### 🛠️ Tech Stack")
                for cat, tech in plan_data.get('tech_stack', {}).items():
                    st.markdown(f"**{cat}:** `{tech}`")
        
        with col_cost:
            with st.container(border=True):
                st.markdown("#### 💰 Cost Analysis")
                for cat, cost in plan_data.get('cost_analysis', {}).items():
                    st.markdown(f"**{cat}:** `{cost}`")

        # Folder Structure Visualization
        st.markdown("### 📂 Proposed Folder Structure")
        with st.container(border=True):
            cols = st.columns(len(plan_data.get('folder_structure', {})) or 1)
            for i, (folder, files) in enumerate(plan_data.get('folder_structure', {}).items()):
                with cols[i % len(cols)]:
                    st.markdown(f"**📁 {folder}/**")
                    for file in files:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📄 {file}")

        st.markdown("### 📋 Task Board")
        for task in plan_data['tasks']:
            with st.expander(f"Task {task['id']}: {task['title']} - [{task['status'].upper()}]"):
                col_left, col_right = st.columns([3, 1])
                
                with col_left:
                    st.write(task['description'])
                    st.caption(f"Agent Assigned: `{task['agent_type']}`")
                
                with col_right:
                    status_options = ["pending", "in_progress", "completed"]
                    idx = status_options.index(task['status']) if task['status'] in status_options else 0
                    
                    new_status = st.selectbox("Update Status", status_options, index=idx, key=f"up_{task['id']}")
                    if new_status != task['status']:
                        sm.update_task_status(task['id'], new_status)
                        st.rerun()
    else:
        st.warning("Belum ada rencana aktif.")

elif menu == "Create New Project":
    st.title("➕ Create New Project")
    st.markdown("---")
    
    col_input, col_config = st.columns([2, 1])
    
    with col_input:
        st.write("#### 1. Deskripsi Proyek")
        user_input = st.text_area("Apa yang ingin Anda bangun?", placeholder="Contoh: Aplikasi E-commerce multiflatform...", height=250)
    
    with col_config:
        st.write("#### 2. Konfigurasi Teknis")
        platforms = st.multiselect("Platform Target", ["Android", "iOS", "Web", "Desktop"], default=["Android", "iOS"])
        db_pref = st.selectbox("Database Utama", ["Firebase (Recommended)", "Supabase", "PostgreSQL", "MongoDB"])
        
        st.write("#### 3. Git & Connectivity")
        git_url = st.text_input("Remote Git URL", placeholder="https://github.com/user/repo.git")
        
        if st.button("🔍 Verifikasi Konektivitas & API", use_container_width=True):
            has_keys = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if has_keys:
                st.success("✅ Environment Ready!")
            else:
                st.error("❌ API Keys missing in .env")

    st.markdown("---")
    if st.button("🚀 Generate Rencana Project Sekarang", use_container_width=True):
        if user_input:
            constraints = {"platforms": platforms, "db": db_pref, "git": git_url}
            with st.spinner("AI sedang merancang sistem, biaya, dan struktur folder..."):
                try:
                    new_plan = orch.create_plan(user_input, constraints=constraints)
                    sm.save_plan(new_plan)
                    st.success(f"Berhasil merancang: {new_plan.project_name}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Gagal merancang: {e}")

elif menu == "Project History":
    st.title("📂 Project History")
    st.markdown("---")
    all_plans = get_all_plans()
    if all_plans:
        selected_file = st.selectbox("Pilih Rencana Lama", all_plans)
        if selected_file:
            filepath = os.path.join("docs/brain", selected_file)
            with open(filepath, 'r') as f:
                history_data = json.load(f)
            
            st.header(f"Project: {history_data['project_name']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Jadikan Rencana Aktif", use_container_width=True):
                    with open(os.path.join("docs/brain", "latest_plan.json"), 'w') as f:
                        json.dump(history_data, f, indent=4)
                    st.rerun()
            with c2:
                if st.checkbox("Konfirmasi Hapus"):
                    if st.button("Hapus Permanen", type="primary", use_container_width=True):
                        os.remove(filepath)
                        st.rerun()
            st.json(history_data)
