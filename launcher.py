import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import os

class LISLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("EWC LIS Controller")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        self.backend_process = None
        self.middleware_process = None

        # UI Elements
        title = tk.Label(root, text="EWC LIS Server Manager", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        self.btn_start = tk.Button(btn_frame, text="START SYSTEM", bg="green", fg="white", font=("Arial", 12), width=20, command=self.start_system)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="STOP SYSTEM", bg="red", fg="white", font=("Arial", 12), width=20, command=self.stop_system, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.log_area = scrolledtext.ScrolledText(root, width=70, height=15, font=("Consolas", 9))
        self.log_area.pack(pady=10)

        self.log("Ready to launch...")

    def log(self, message):
        self.log_area.insert(tk.END, f">> {message}\n")
        self.log_area.see(tk.END)

    def start_system(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Start Backend (API)
        api_path = os.path.join(os.getcwd(), "backend")
        self.log("Starting API Server...")
        self.backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=api_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        # Start Middleware (Listener)
        mw_path = os.path.join(os.getcwd(), "middleware")
        self.log("Starting Machine Listener...")
        self.middleware_process = subprocess.Popen(
            [sys.executable, "listener.py"],
            cwd=mw_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        self.log("System Running.")

    def stop_system(self):
        if self.backend_process:
            self.backend_process.terminate()
        if self.middleware_process:
            self.middleware_process.terminate()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.log("System Stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LISLauncher(root)
    root.mainloop()