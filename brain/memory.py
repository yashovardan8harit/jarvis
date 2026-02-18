class ConversationMemory:
    def __init__(self, max_history=6):
        self.history = []
        self.max_history = max_history

    def add_user_message(self, message):
        self.history.append(f"User: {message}")
        self._trim()

    def add_assistant_message(self, message):
        self.history.append(f"Jarvis: {message}")
        self._trim()

    def get_context(self):
        return "\n".join(self.history)

    def _trim(self):
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
