import subprocess
from brain.memory import ConversationMemory
import json

memory = ConversationMemory()

class LocalLLM:
    def __init__(self, model_name="qwen2.5:3b"):
        self.model = model_name

    import json

    def generate_system_command(self, user_prompt):
        try:
            system_prompt = """
You are Jarvis system command parser.

Convert the user request into a JSON object.

Allowed actions:
- open_drive
- open_folder
- create_folder
- create_word_file
- open_app

Return ONLY valid JSON.
If multiple steps exist, return a list under "actions".

Examples:

User: open d drive and open project
{
  "actions": [
    {"action": "open_drive", "value": "D"},
    {"action": "open_folder", "value": "project"}
  ]
}

User: create word file named yash in project in d drive
{
  "actions": [
    {"action": "open_drive", "value": "D"},
    {"action": "open_folder", "value": "project"},
    {"action": "create_word_file", "value": "yash"}
  ]
}
"""

            full_prompt = system_prompt + "\nUser: " + user_prompt

            result = subprocess.run(
                ["ollama", "run", self.model, full_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            response = result.stdout.strip()

            return json.loads(response)

        except Exception as e:
            return None


    def generate(self, user_prompt):
        try:
            system_prompt = (
                "You are Jarvis, a concise desktop AI assistant. "
                "Respond naturally in conversational plain text. "
                "No markdown. Keep responses suitable for speech."
            )

            memory.add_user_message(user_prompt)

            context = memory.get_context()

            full_prompt = f"{system_prompt}\n\n{context}\nJarvis:"

            result = subprocess.run(
                ["ollama", "run", self.model, full_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            response = result.stdout.strip()

            memory.add_assistant_message(response)

            return response

        except Exception as e:
            return f"Error communicating with LLM: {e}"