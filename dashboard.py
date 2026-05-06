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

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .project-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        transition: 0.3s;
    }
    .project-card:hover {
        border-color: #58a6ff;
        background-color: #21262d;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Managers
sm = StateManager()
orch = Orchestrator()

# Helper Functions
def get_all_plans():
    plans = glob.glob(os.path.join("docs/brain", "plan_*.json"))
    plans.sort(reverse=True)
    return plans

def load_plan(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# Sidebar
st.sidebar.title("🦾 Core Engine Orc")
menu = st.sidebar.radio("Navigation", ["Project List", "Create New Project"])

# Session State for Routing
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

# --- ROUTING ---

if menu == "Project List":
    if st.session_state.selected_project is None:
        st.title("📂 My Projects")
        st.markdown("---")
        
        plans = get_all_plans()
        if not plans:
            st.info("Belum ada proyek. Silakan buat proyek baru di menu sebelah kiri.")
        else:
            # Grid layout for project cards
            for plan_path in plans:
                data = load_plan(plan_path)
                filename = os.path.basename(plan_path)
                
                with st.container(border=True):
                    col_info, col_actions = st.columns([4, 1])
                    with col_info:
                        st.subheader(f"📁 {data['project_name']}")
                        st.write(f"_{filename}_")
                        # Show first task as a description or a summary if available
                        st.caption(f"Total Tasks: {data['total_tasks']} | Database: {data.get('tech_stack', {}).get('Database', 'N/A')}")
                    
                    with col_actions:
                        if st.button("View Details", key=f"view_{filename}", use_container_width=True):
                            st.session_state.selected_project = plan_path
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"del_{filename}", use_container_width=True, type="secondary"):
                            os.remove(plan_path)
                            st.success(f"Project {data['project_name']} dihapus.")
                            st.rerun()
    else:
        # DETAIL VIEW
        plan_data = load_plan(st.session_state.selected_project)
        
        if st.button("⬅️ Back to Project List"):
            st.session_state.selected_project = None
            st.rerun()
            
        st.title(f"🚀 {plan_data['project_name']}")
        st.markdown("---")
        
        # Metrics & Info
        completed = sum(1 for t in plan_data['tasks'] if t['status'] == 'completed')
        total = plan_data['total_tasks']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Tasks Completed", f"{completed}/{total}")
        c2.metric("Budget Insight", plan_data.get('cost_analysis', {}).get('Total', 'N/A'))
        c3.metric("Platform", ", ".join(plan_data.get('tech_stack', {}).get('Frontend', 'N/A').split(',')))
        
        st.progress(completed/total)
        
        # Tech & Cost Panels
        col_t, col_c = st.columns(2)
        with col_t:
            with st.container(border=True):
                st.markdown("#### 🛠️ Tech Stack")
                for k, v in plan_data.get('tech_stack', {}).items():
                    st.markdown(f"**{k}:** `{v}`")
        with col_c:
            with st.container(border=True):
                st.markdown("#### 💰 Cost Analysis")
                for k, v in plan_data.get('cost_analysis', {}).items():
                    st.markdown(f"**{k}:** `{v}`")

        # Folder Structure
        st.markdown("### 📂 Folder Structure")
        with st.container(border=True):
            cols = st.columns(3)
            for i, (folder, files) in enumerate(plan_data.get('folder_structure', {}).items()):
                with cols[i % 3]:
                    st.markdown(f"**📁 {folder}/**")
                    for f in files: st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📄 {f}")

        # Tasks
        st.markdown("### 📋 Tasks")
        
        # Form to add new task
        with st.expander("➕ Add New Task / Module"):
            new_title = st.text_input("Task Title")
            new_desc = st.text_area("Task Description")
            new_agent = st.selectbox("Agent Type", ["coder", "researcher", "reviewer"])
            if st.button("Add Task to Project"):
                if new_title and new_desc:
                    new_id = max([t['id'] for t in plan_data['tasks']]) + 1 if plan_data['tasks'] else 1
                    plan_data['tasks'].append({
                        "id": new_id,
                        "title": new_title,
                        "description": new_desc,
                        "agent_type": new_agent,
                        "status": "pending",
                        "dependencies": []
                    })
                    plan_data['total_tasks'] = len(plan_data['tasks'])
                    with open(st.session_state.selected_project, 'w') as f:
                        json.dump(plan_data, f, indent=4)
                    st.success(f"Tugas baru '{new_title}' berhasil ditambahkan!")
                    st.rerun()

        for task in plan_data['tasks']:
            with st.expander(f"Task {task['id']}: {task['title']} ({task['status']})"):
                # Editable Fields
                edited_title = st.text_input("Title", value=task['title'], key=f"title_{task['id']}")
                edited_desc = st.text_area("Description", value=task['description'], key=f"desc_{task['id']}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    new_status = st.selectbox("Update Status", ["pending", "in_progress", "completed"], 
                                            index=["pending", "in_progress", "completed"].index(task['status']),
                                            key=f"status_{task['id']}")
                with c_b:
                    new_agent = st.selectbox("Agent Type", ["coder", "researcher", "reviewer"],
                                            index=["coder", "researcher", "reviewer"].index(task['agent_type']),
                                            key=f"agent_{task['id']}")
                
                if st.button("Save Changes", key=f"save_{task['id']}"):
                    task['title'] = edited_title
                    task['description'] = edited_desc
                    task['status'] = new_status
                    task['agent_type'] = new_agent
                    with open(st.session_state.selected_project, 'w') as f:
                        json.dump(plan_data, f, indent=4)
                    st.success("Perubahan disimpan!")
                    st.rerun()

elif menu == "Create New Project":
    st.title("➕ Create New Project")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("#### 1. Deskripsi Proyek")
        user_input = st.text_area("Apa yang ingin Anda bangun?", height=250)
    with col2:
        st.write("#### 2. Konfigurasi Teknis")
        platforms = st.multiselect("Platform", ["Android", "iOS", "Web", "Desktop"], default=["Android", "iOS"])
        db_pref = st.selectbox("Database", ["Firebase", "Supabase", "PostgreSQL", "MongoDB"])
        backend_pref = st.selectbox("Backend", ["FastAPI", "Go", "Node.js", "Firebase Functions"])
        
    if st.button("🚀 Generate Rencana", use_container_width=True):
        if user_input:
            with st.spinner("AI sedang merancang..."):
                constraints = {"platforms": platforms, "db": db_pref, "backend": backend_pref}
                new_plan = orch.create_plan(user_input, constraints=constraints)
                sm.save_plan(new_plan)
                st.success("Berhasil! Silakan cek di Project List.")
                st.balloons()
