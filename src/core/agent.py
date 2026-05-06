import os
import subprocess
from typing import List, Dict, Any
from src.core.adapter import AIAdapter

class SubAgent:
    """
    SubAgent is responsible for executing specific tasks using tools.
    It can write files, run terminal commands, and read project context.
    """
    
    def __init__(self, agent_type: str = "coder", adapter: AIAdapter = None, base_dir: str = "."):
        self.agent_type = agent_type
        self.adapter = adapter or AIAdapter()
        self.base_dir = base_dir
        self.history = []
        
        # Pastikan folder sandbox ada
        os.makedirs(self.base_dir, exist_ok=True)

    def execute_task(self, task_title: str, task_description: str, context: str = "", max_retries: int = 3) -> Dict[str, Any]:
        """
        Executes a task with Self-Healing capabilities (auto-retry on failure).
        """
        current_attempt = 0
        last_error = ""
        full_log = []

        while current_attempt < max_retries:
            current_attempt += 1
            
            # Tambahkan konteks error jika ini adalah percobaan ulang
            error_context = f"\nPREVIOUS ERROR:\n{last_error}\nPlease analyze the error and try a different approach or fix the code." if last_error else ""
            
            prompt = f"""
            You are a specialized AI Sub-Agent ({self.agent_type}).
            Task: {task_title}
            Description: {task_description}
            Attempt: {current_attempt}/{max_retries}
            
            Project Context:
            {context}
            {error_context}
            
            Instructions:
            1. Analyze the task and any previous errors.
            2. Use WRITE_FILE to fix/create code or RUN_COMMAND to execute.
            3. You MUST follow this format EXACTLY:

            THOUGHT: [Your reasoning and error analysis]
            ACTION: [WRITE_FILE | RUN_COMMAND | READ_FILE | NONE]
            PARAM: [Filename path or command string]
            CONTENT: [The code or content to write]
            RESULT: [Summary of this attempt]
            """
            
            response = self.adapter.chat(prompt)
            res_text = response if isinstance(response, str) else str(response)
            
            # --- PARSING ---
            action, param, content = self._parse_response(res_text)
            
            # --- EXECUTION ---
            execution_log = ""
            if action == "WRITE_FILE" and param:
                execution_log = self.write_file(param, content)
            elif action == "RUN_COMMAND" and param:
                execution_log = self.run_command(param)
            elif action == "READ_FILE" and param:
                execution_log = self.read_file(param)
            else:
                execution_log = "No action taken."

            full_log.append({
                "attempt": current_attempt,
                "thought": res_text.split("ACTION:")[0].replace("THOUGHT:", "").strip(),
                "action": action,
                "log": execution_log
            })

            # Check for success
            if "Success" in execution_log:
                return {
                    "status": "success",
                    "attempts": current_attempt,
                    "execution_log": execution_log,
                    "thought": full_log[-1]["thought"],
                    "action": action,
                    "param": param,
                    "full_history": full_log
                }
            
            # If failed, store error and loop
            last_error = execution_log
            print(f"[SELF-HEALING] Attempt {current_attempt} failed. Retrying...")

        return {
            "status": "failed",
            "attempts": max_retries,
            "execution_log": last_error,
            "thought": "All attempts failed.",
            "full_history": full_log
        }

    def _parse_response(self, text: str):
        lines = text.split("\n")
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
        
        return action, param, "\n".join(content_lines).strip()

    # --- TOOLS ---
    
    def write_file(self, file_path: str, content: str) -> str:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: File {file_path} written inside {self.base_dir}."
        except Exception as e:
            return f"Error: {str(e)}"

    def run_command(self, command: str) -> str:
        try:
            # Jalankan perintah di dalam folder base_dir
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=self.base_dir)
            if result.returncode == 0:
                return f"Success:\n{result.stdout}"
            else:
                return f"Error:\n{result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, file_path: str) -> str:
        try:
            full_path = os.path.join(self.base_dir, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

class CriticAgent:
    """
    CriticAgent reviews the work of SubAgents.
    It provides a score and feedback to ensure high quality.
    """
    def __init__(self, adapter: AIAdapter = None):
        self.adapter = adapter or AIAdapter()

    def review_task(self, task_title: str, task_desc: str, agent_output: str, execution_log: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Senior Quality Assurance Engineer & Code Reviewer.
        Task: {task_title}
        Original Goal: {task_desc}
        
        Agent Execution Output:
        {agent_output}
        
        Execution Log:
        {execution_log}
        
        Instructions:
        1. Evaluate if the agent successfully achieved the goal.
        2. Check for bugs, security risks, or missing requirements.
        3. Provide a Score from 1 to 10.
        
        Format your response EXACTLY like this:
        SCORE: [1-10]
        CRITIQUE: [Your detailed feedback]
        SUGGESTIONS: [Specific steps to fix the issues]
        FINAL_VERDICT: [PASS | FAIL]
        """
        
        response = self.adapter.chat(prompt)
        res_text = response if isinstance(response, str) else str(response)
        
        # Simple Parsing
        lines = res_text.split("\n")
        score = 0
        verdict = "FAIL"
        
        for line in lines:
            if line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip().split("/")[0])
                except:
                    score = 5
            if line.startswith("FINAL_VERDICT:"):
                verdict = line.replace("FINAL_VERDICT:", "").strip()

        return {
            "score": score,
            "verdict": verdict,
            "raw_review": res_text
        }

if __name__ == "__main__":
    # Quick Test
    agent = SubAgent()
    print("Testing Agent Tool: write_file")
    print(agent.write_file("docs/tests/test_agent.txt", "Hello from SubAgent!"))
    print("Testing Agent Tool: run_command")
    print(agent.run_command("dir"))
