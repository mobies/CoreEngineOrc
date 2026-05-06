import streamlit as st
import json
import os
from src.core.state import StateManager

# Page Configuration
st.set_page_config(
    page_title="Core Engine Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize State Manager
sm = StateManager()

def load_data():
    return sm.load_latest_plan()

# Sidebar
st.sidebar.title("🤖 Core Engine")
st.sidebar.markdown("---")
st.sidebar.info("Dashboard ini digunakan untuk memantau dan mengelola rencana kerja AI Orchestrator.")

# Main Header
st.title("🚀 Project Dashboard")
st.markdown("---")

# Load Data
plan = load_data()

if plan:
    # Project Header Info
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"Project: {plan['project_name']}")
    with col2:
        completed_tasks = sum(1 for t in plan['tasks'] if t['status'] == 'completed')
        total_tasks = plan['total_tasks']
        progress = completed_tasks / total_tasks
        st.metric("Total Progress", f"{int(progress * 100)}%", delta=f"{completed_tasks}/{total_tasks} Tasks")
        st.progress(progress)

    st.markdown("### 📋 Task List")
    
    # Display Tasks
    for task in plan['tasks']:
        with st.expander(f"Task {task['id']}: {task['title']}", expanded=(task['status'] != 'completed')):
            c1, c2, c3 = st.columns([3, 1, 1])
            
            with c1:
                st.markdown(f"**Description:**\n{task['description']}")
                if task['dependencies']:
                    st.caption(f"⛓️ Dependencies: Task {task['dependencies']}")
            
            with c2:
                st.markdown(f"**Agent Type:**\n`{task['agent_type']}`")
            
            with c3:
                # Status Selector
                status_options = ["pending", "in_progress", "completed"]
                current_index = status_options.index(task['status']) if task['status'] in status_options else 0
                
                new_status = st.selectbox(
                    "Update Status",
                    options=status_options,
                    index=current_index,
                    key=f"status_{task['id']}"
                )
                
                if new_status != task['status']:
                    sm.update_task_status(task['id'], new_status)
                    st.rerun()

    if st.button("Refresh Data"):
        st.rerun()

else:
    st.warning("Belum ada rencana proyek yang terdeteksi. Silakan jalankan Orchestrator terlebih dahulu.")
    if st.button("Simulasi Buat Rencana"):
        st.info("Fitur ini akan segera hadir!")

# Footer
st.markdown("---")
st.caption("Powered by Core Engine Orchestrator | Gemini 3 Flash")
