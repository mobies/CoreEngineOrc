import streamlit as st
import json
import os
import glob
from datetime import datetime
from dotenv import load_dotenv
from src.core.state import StateManager
from src.core.orchestrator import Orchestrator

# Load local environment variables
load_dotenv()

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

# --- LOGIN PROTECTION ---
def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    # Jika sudah login sebelumnya dalam sesi ini, langsung lolos
    if st.session_state.password_correct:
        return True

    # Ambil password dari Secrets (Cloud) atau Env (Local)
    correct_password = os.getenv("DASHBOARD_PASSWORD")
    try:
        if "DASHBOARD_PASSWORD" in st.secrets:
            correct_password = st.secrets["DASHBOARD_PASSWORD"]
    except:
        pass

    # Jika password tidak diset, bebaskan akses
    if not correct_password:
        st.session_state.password_correct = True
        return True

    # Tampilan Form Login
    st.title("🔐 Core Engine - Locked")
    with st.form("login_form"):
        password_input = st.text_input("Masukkan Password Dashboard", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if password_input.strip() == correct_password.strip():
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Password salah!")
    return False

if not check_password():
    st.stop() # Hentikan eksekusi jika belum login

try:
    orch = Orchestrator()
    orch_error = None
except Exception as e:
    orch = None
    orch_error = str(e)

# Helper Functions
def get_all_plans():
    # Mengambil daftar dari Cloud/Lokal via StateManager
    filenames = sm.list_all_projects()
    filenames.sort(reverse=True)
    # Mengembalikan path lengkap agar bisa dibaca load_plan
    return [os.path.join("docs/brain", f) for f in filenames]

def load_plan(filepath):
    if not os.path.exists(filepath):
        # Jika file tidak ada (mungkin baru didelete di cloud), return None
        return None
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
    if orch_error:
        st.error(f"⚠️ **Konfigurasi AI Gagal:** {orch_error}")
        st.info("Pastikan GOOGLE_API_KEY sudah dimasukkan ke dalam .env (Lokal) atau Streamlit Secrets (Cloud).")
    
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
                if not data: continue # Skip jika file tidak valid
                
                filename = os.path.basename(plan_path)
                
                with st.container(border=True):
                    col_info, col_actions = st.columns([4, 1])
                    with col_info:
                        st.subheader(f"📁 {data['project_name']}")
                        st.write(f"_{filename}_")
                        st.caption(f"Total Tasks: {data['total_tasks']} | Database: {data.get('tech_stack', {}).get('Database', 'N/A')}")
                    
                    with col_actions:
                        if st.button("View Details", key=f"view_{filename}", use_container_width=True):
                            st.session_state.selected_project = plan_path
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"del_{filename}", use_container_width=True, type="secondary"):
                            sm.delete_project(filename)
                            st.success(f"Project dihapus.")
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
            
            # Insertion Position
            task_titles = [f"ID {t['id']}: {t['title']}" for t in plan_data['tasks']]
            insert_after = st.selectbox("Insert After Task", ["(At the End)"] + task_titles)
            
            if st.button("Add Task to Project"):
                if new_title and new_desc:
                    new_id = max([t['id'] for t in plan_data['tasks']]) + 1 if plan_data['tasks'] else 1
                    new_task = {
                        "id": new_id,
                        "title": new_title,
                        "description": new_desc,
                        "agent_type": new_agent,
                        "status": "pending",
                        "dependencies": []
                    }
                    
                    if insert_after == "(At the End)":
                        plan_data['tasks'].append(new_task)
                    else:
                        # Find index of the selected task
                        after_id = int(insert_after.split(":")[0].replace("ID ", ""))
                        idx = next(i for i, t in enumerate(plan_data['tasks']) if t['id'] == after_id)
                        plan_data['tasks'].insert(idx + 1, new_task)
                    
                    plan_data['total_tasks'] = len(plan_data['tasks'])
                    with open(st.session_state.selected_project, 'w') as f:
                        json.dump(plan_data, f, indent=4)
                    st.success(f"Tugas baru berhasil disisipkan!")
                    st.rerun()

        for task in plan_data['tasks']:
            with st.expander(f"Task {task['id']}: {task['title']} ({task['status']})"):
                # Editable Fields
                edited_title = st.text_input("Title", value=task['title'], key=f"title_{task['id']}")
                edited_desc = st.text_area("Description", value=task['description'], key=f"desc_{task['id']}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    status_list = ["pending", "in_progress", "completed"]
                    current_status = task.get('status', 'pending')
                    if current_status not in status_list:
                        current_status = 'pending'
                        
                    new_status = st.selectbox("Update Status", status_list, 
                                            index=status_list.index(current_status),
                                            key=f"status_{task['id']}")
                with c_b:
                    agent_list = ["coder", "researcher", "reviewer"]
                    current_agent = task.get('agent_type', 'coder')
                    if current_agent not in agent_list:
                        current_agent = 'coder'
                    
                    new_agent = st.selectbox("Agent Type", agent_list,
                                            index=agent_list.index(current_agent),
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
                
                st.markdown("---")
                if st.button(f"⚡ Execute Task {task['id']}", key=f"exec_{task['id']}", use_container_width=True, type="primary"):
                    from src.core.agent import SubAgent
                    
                    # Tentukan folder Sandbox (projects/nama_project)
                    project_folder = os.path.join("projects", plan_data['project_name'].lower().replace(" ", "_"))
                    agent = SubAgent(agent_type=task['agent_type'], base_dir=project_folder)
                    
                    # Update status ke in_progress segera
                    task['status'] = 'in_progress'
                    with open(st.session_state.selected_project, 'w') as f:
                        json.dump(plan_data, f, indent=4)
                    
                    with st.spinner(f"Agent sedang bekerja..."):
                        try:
                            # --- QUALITY LOOP (Max 2 revisions) ---
                            max_revisions = 2
                            current_rev = 0
                            feedback = ""
                            
                            while current_rev <= max_revisions:
                                context = f"Project Structure: {json.dumps(plan_data.get('folder_structure', {}))}"
                                if feedback:
                                    context += f"\n\nCRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}"
                                
                                # Execute Task
                                result = agent.execute_task(task['title'], task['description'], context=context)
                                
                                # Review Task
                                critic = CriticAgent()
                                review = critic.review_task(task['title'], task['description'], result['output'], result['execution_log'])
                                result['review'] = review
                                
                                # Simpan hasil terbaru
                                st.session_state[f"last_result_{task['id']}"] = result
                                
                                # Jika skor bagus atau sudah mentok revisi, keluar loop
                                if review['score'] >= 7 or current_rev == max_revisions:
                                    break
                                
                                # Jika skor buruk, siapkan feedback dan ulangi
                                feedback = review['raw_review']
                                current_rev += 1
                                st.warning(f"Skor rendah ({review['score']}/10). Meminta revisi ke-{current_rev}...")
                            
                            # Update status final (set to completed tapi minta approval di UI)
                            task['status'] = 'completed'
                            with open(st.session_state.selected_project, 'w') as f:
                                json.dump(plan_data, f, indent=4)
                            st.success(f"Agen telah menyelesaikan tugas! Silakan review dan Approve.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Eksekusi Gagal: {e}")

                # Tampilkan hasil eksekusi terakhir jika ada di session state
                if f"last_result_{task['id']}" in st.session_state:
                    res = st.session_state[f"last_result_{task['id']}"]
                    with st.container(border=True):
                        st.markdown(f"#### 🤖 Last Agent Report ({res.get('status', 'N/A')})")
                        
                        # Display Review
                        if 'review' in res:
                            rev = res['review']
                            score = rev.get('score', 0)
                            color = "green" if score >= 8 else "orange" if score >= 5 else "red"
                            st.markdown(f"**Quality Score:** :{color}[{score}/10]")
                            with st.expander("🔍 View Critic Feedback"):
                                st.write(rev.get('raw_review', 'No detail'))
                        
                        # Approval Button
                        if task['status'] == 'completed' and not task.get('finalized', False):
                            if st.button(f"✅ Approve & Finalize Task {task['id']}", key=f"app_{task['id']}", use_container_width=True):
                                task['finalized'] = True
                                with open(st.session_state.selected_project, 'w') as f:
                                    json.dump(plan_data, f, indent=4)
                                st.success("Task Finalized!")
                                st.rerun()
                        elif task.get('finalized'):
                            st.success("🌟 Task Finalized & Approved")
                        
                        st.write(f"**Attempts:** {res.get('attempts', 1)}")
                        st.write(f"**Last Thought:** {res.get('thought', 'N/A')}")
                        
                        with st.expander("View Full History & Logs"):
                            for entry in res.get('full_history', []):
                                st.markdown(f"**Attempt {entry['attempt']} - Action: `{entry['action']}`**")
                                st.code(entry['log'])

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
