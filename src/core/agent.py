import os
import subprocess
from typing import List, Dict, Any
from src.core.adapter import AIAdapter

class SubAgent:
    """
    SubAgent is responsible for executing specific tasks using tools.
    It can write files, run terminal commands, and read project context.
    """
    
    def __init__(self, agent_type: str = "coder", adapter: AIAdapter = None):
        self.agent_type = agent_type
        self.adapter = adapter or AIAdapter()
        self.history = []

    def execute_task(self, task_title: str, task_description: str, context: str = "") -> Dict[str, Any]:
        """
        Executes a specific task by thinking, acting, and observing.
        """
        prompt = f"""
        You are a specialized AI Sub-Agent ({self.agent_type}).
        Task: {task_title}
        Description: {task_description}
        
        Project Context:
        {context}
        
        Instructions:
        1. Analyze the task.
        2. If you need to write code, use the WRITE_FILE action.
        3. If you need to run a command, use the RUN_COMMAND action.
        4. You MUST follow this format EXACTLY:

        THOUGHT: [Your reasoning]
        ACTION: [WRITE_FILE | RUN_COMMAND | READ_FILE | NONE]
        PARAM: [Filename path or command string]
        CONTENT: [The code or content to write, or leave empty for others]
        RESULT: [A brief summary of what you intend to do]
        """
        
        response = self.adapter.chat(prompt)
        res_text = response.content if hasattr(response, 'content') else str(response)
        
        # --- PARSING & EXECUTION ---
        lines = res_text.split("\n")
        action = "NONE"
        param = ""
        content_lines = []
        is_content = False
        
        for line in lines:
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("PARAM:"):
                param = line.replace("PARAM:", "").strip()
            elif line.startswith("CONTENT:"):
                is_content = True
                content_lines.append(line.replace("CONTENT:", "").strip())
            elif line.startswith("RESULT:"):
                is_content = False
            elif is_content:
                content_lines.append(line)
        
        content = "\n".join(content_lines).strip()
        execution_log = ""
        
        if action == "WRITE_FILE" and param:
            execution_log = self.write_file(param, content)
        elif action == "RUN_COMMAND" and param:
            execution_log = self.run_command(param)
        elif action == "READ_FILE" and param:
            execution_log = self.read_file(param)
        else:
            execution_log = "No specific system action taken or action unrecognized."

        return {
            "agent": self.agent_type,
            "status": "completed",
            "thought": res_text.split("ACTION:")[0].replace("THOUGHT:", "").strip(),
            "action": action,
            "param": param,
            "execution_log": execution_log,
            "output": res_text
        }

    # --- TOOLS ---
    
    def write_file(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: File {file_path} written."
        except Exception as e:
            return f"Error: {str(e)}"

    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return f"Success:\n{result.stdout}"
            else:
                return f"Error:\n{result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Quick Test
    agent = SubAgent()
    print("Testing Agent Tool: write_file")
    print(agent.write_file("docs/tests/test_agent.txt", "Hello from SubAgent!"))
    print("Testing Agent Tool: run_command")
    print(agent.run_command("dir"))
