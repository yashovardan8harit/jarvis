import os
import subprocess
from docx import Document

class SystemControl:

    ALLOWED_DRIVES = ["C:", "D:", "E:"]

    def __init__(self):
        self.current_path = None

    # =========================
    # POWER CONTROLS
    # =========================
    def shutdown(self):
        os.system("shutdown /s /t 5")

    def restart(self):
        os.system("shutdown /r /t 5")

    def lock(self):
        os.system("rundll32.exe user32.dll,LockWorkStation")

    def sleep(self):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    # =========================
    # APP CONTROL
    # =========================
    def open_app(self, app_name):
        try:
            if app_name == "chrome":
                os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

            elif app_name == "code":
                os.startfile("C:\\Users\\Yashovardhan Harit\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")

            else:
                os.startfile(app_name)

        except Exception as e:
            print(f"Could not open {app_name}: {e}")

    # =========================
    # DRIVE / FOLDER CONTROL
    # =========================
    def open_drive(self, drive_letter):
        drive = drive_letter.upper() + ":"

        if drive not in self.ALLOWED_DRIVES:
            return "Drive not allowed"

        path = drive + "\\"
        os.startfile(path)
        self.current_path = path
        return f"Opening {drive} drive"

    def open_folder(self, folder_name):
        if not self.current_path:
            return "Please open a drive first."

        path = os.path.join(self.current_path, folder_name)

        if os.path.exists(path):
            os.startfile(path)
            self.current_path = path
            return f"Opening folder {folder_name}"
        else:
            return "Folder not found"

    def create_folder(self, folder_name):
        if not self.current_path:
            return "Please open a drive or folder first."

        path = os.path.join(self.current_path, folder_name)
        os.makedirs(path, exist_ok=True)
        return f"Folder {folder_name} created"

    def create_word_file(self, file_name):
        if not self.current_path:
            return "Please open a directory first."

        file_path = os.path.join(self.current_path, file_name + ".docx")

        doc = Document()
        doc.add_paragraph("Created by Jarvis")
        doc.save(file_path)

        return f"Word file {file_name} created"
