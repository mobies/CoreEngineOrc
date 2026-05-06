import json
from typing import List, Dict
from pydantic import BaseModel, Field
from .adapter import AIAdapter

class Task(BaseModel):
    id: int
    title: str
    description: str
    agent_type: str = Field(description="Jenis agen yang cocok (misal: coder, researcher, reviewer)")
    dependencies: List[int] = Field(default_factory=list, description="ID tugas yang harus selesai lebih dulu")
    status: str = Field(default="pending", description="Status tugas (pending, in_progress, completed)")

class ProjectPlan(BaseModel):
    project_name: str
    total_tasks: int
    tasks: List[Task]
    tech_stack: Dict[str, str]
    cost_analysis: Dict[str, str]
    folder_structure: Dict[str, List[str]] = Field(description="Struktur folder dan file yang diusulkan")

ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Master Orchestrator for Multiplatform Application Development. 
Your goal is to design cutting-edge systems and their exact file structures.

Your output MUST be a valid JSON object matching this EXACT schema:
{
  "project_name": "Name",
  "total_tasks": 3,
  "tasks": [
    {
      "id": 1, 
      "title": "Task Title",
      "description": "Details",
      "agent_type": "coder/researcher/reviewer",
      "dependencies": []
    }
  ],
  "tech_stack": {"Category": "Technology"},
  "cost_analysis": {"Category": "Cost Estimate"},
  "folder_structure": {"Folder": ["file.ext", "subfolder/"]}
}

CRITICAL: 
- Use 'id' (integer), NOT 'step'.
- Every task MUST have an 'agent_type'.
- Every task MUST have a 'status' (default to 'pending').

Always prioritize standard clean architecture patterns.
Response ONLY with the JSON object.
"""

class Orchestrator:
    def __init__(self, adapter: AIAdapter = None):
        self.adapter = adapter or AIAdapter()
        
    def create_plan(self, user_request: str, constraints: Dict = None) -> ProjectPlan:
        """
        Translates user request into a structured ProjectPlan with constraints.
        """
        constraint_str = f"\nUser Constraints: {json.dumps(constraints)}" if constraints else ""
        full_prompt = f"{ORCHESTRATOR_SYSTEM_PROMPT}\n\nUser Request: {user_request}{constraint_str}"
        
        # Call AI through the adapter
        response = self.adapter.chat(full_prompt)
        
        # Handle different response formats (String vs Message Object)
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, dict) and 'content' in response:
            content = response['content']
        else:
            content = str(response)

        # If content is a list (multimodal or multi-part), join it
        if isinstance(content, list):
            content = "".join([str(part.get('text', part)) if isinstance(part, dict) else str(part) for part in content])

        content = content.strip()
        
        # Clean response content (remove markdown json blocks)
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        try:
            plan_data = json.loads(content)
            
            # --- AUTO-FIX LOGIC ---
            # Fix 'step' -> 'id' and missing 'agent_type'
            for task in plan_data.get('tasks', []):
                if 'step' in task and 'id' not in task:
                    task['id'] = task['step']
                if 'agent_type' not in task:
                    task['agent_type'] = "coder" # Default fallback
                if 'status' not in task:
                    task['status'] = "pending"
            
            return ProjectPlan(**plan_data)
        except Exception as e:
            raise ValueError(f"Failed to parse ProjectPlan: {e}\nRaw Content: {content}")

if __name__ == "__main__":
    # Quick test for Orchestrator
    orch = Orchestrator()
    print("--- Orchestrator Planning Test ---")
    request = "Buatlah landing page sederhana untuk toko kopi menggunakan HTML dan CSS."
    plan = orch.create_plan(request)
    
    print(f"Project: {plan.project_name}")
    for task in plan.tasks:
        print(f"[{task.id}] {task.title} (Agent: {task.agent_type})")
        print(f"    - {task.description}")
