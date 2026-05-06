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

ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Master Orchestrator of the Core Engine. Your goal is to translate user intent into a highly structured project execution plan.
You must break down the request into small, actionable tasks that can be performed by specialized sub-agents.

Your output MUST be a valid JSON object following this structure:
{
  "project_name": "Name of the project",
  "total_tasks": 3,
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "Detailed instruction for the sub-agent",
      "agent_type": "coder/researcher/reviewer",
      "dependencies": []
    }
  ]
}

Always prioritize task dependency logic. If a task requires information from another, list its ID in the 'dependencies' array.
Response ONLY with the JSON object. No conversational text.
"""

class Orchestrator:
    def __init__(self, adapter: AIAdapter = None):
        self.adapter = adapter or AIAdapter()
        
    def create_plan(self, user_request: str) -> ProjectPlan:
        """
        Translates user request into a structured ProjectPlan.
        """
        full_prompt = f"{ORCHESTRATOR_SYSTEM_PROMPT}\n\nUser Request: {user_request}"
        
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
