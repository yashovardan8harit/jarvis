import re
from modules.system_control import SystemControl
from brain.llm import LocalLLM

class IntentRouter:

    def __init__(self):
        self.system = SystemControl()
        self.llm = LocalLLM()

    # =========================
    # LLM STRUCTURED EXECUTION
    # =========================
    def execute_structured_actions(self, actions):
        for step in actions:
            action = step.get("action")
            value = step.get("value")

            if action == "open_drive":
                self.system.open_drive(value)

            elif action == "open_folder":
                self.system.open_folder(value)

            elif action == "create_folder":
                self.system.create_folder(value)

            elif action == "create_word_file":
                self.system.create_word_file(value)

            elif action == "open_app":
                self.system.open_app(value)

    # =========================
    # MAIN ROUTER
    # =========================
    def route(self, text):
        text = text.lower()

        # =========================
        # POWER COMMANDS
        # =========================
        if "shutdown" in text or "shut down" in text:
            return {
                "speak": "Shutting down your system.",
                "execute": self.system.shutdown
            }

        if "restart" in text or "re start" in text:
            return {
                "speak": "Restarting your system.",
                "execute": self.system.restart
            }

        if "lock" in text:
            return {
                "speak": "Locking your computer.",
                "execute": self.system.lock
            }

        if "sleep" in text:
            return {
                "speak": "Putting the system to sleep.",
                "execute": self.system.sleep
            }

        # =========================
        # APPLICATION COMMANDS
        # =========================
        if "open chrome" in text:
            return {
                "speak": "Opening Chrome for you.",
                "execute": lambda: self.system.open_app("chrome")
            }

        if "open vs code" in text or "open vscode" in text:
            return {
                "speak": "Opening Visual Studio Code for you.",
                "execute": lambda: self.system.open_app("code")
            }

        if "open teams" in text or "open ms teams" in text:
            return {
                "speak": "Opening Microsoft Teams for you.",
                "execute": lambda: self.system.open_app("teams")
            }

        # =========================
        # BASIC REGEX DRIVE (FAST PATH)
        # =========================
        drive_match = re.search(r'open ([cde]) drive', text)
        if drive_match:
            drive_letter = drive_match.group(1)
            return {
                "speak": f"Opening {drive_letter.upper()} drive.",
                "execute": lambda: self.system.open_drive(drive_letter)
            }

        # =========================
        # FALLBACK → LLM STRUCTURED PARSING
        # =========================
        structured = self.llm.generate_system_command(text)

        if structured and "actions" in structured:

            def executor():
                self.execute_structured_actions(structured["actions"])

            return {
                "speak": "Executing your command.",
                "execute": executor
            }

        return None
