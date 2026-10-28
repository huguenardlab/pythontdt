import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

from experiment_config import EXPERIMENTS, CONTROLLER_SCRIPT
from launcher_app import prepare_experiment


class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TDT Experiment Launcher")
        self.root.geometry("360x240")
        self.root.resizable(False, False)

        tk.Label(root, text="Select an Experiment",
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 10))

        for key, cfg in EXPERIMENTS.items():
            tk.Button(root, text=cfg["description"], width=30, height=2,
                      command=lambda k=key: self.on_select(k)).pack(pady=6)

        self.status = tk.Label(root, text="", fg="gray")
        self.status.pack(pady=(10, 0))

    def on_select(self, exp_key):
        cfg = EXPERIMENTS[exp_key]
        self.status.config(text=f"Preparing {cfg['description']}...")
        self.root.update_idletasks()

        try:
            # 1. Launch OpenWorkbench, connect, apply startup tags.
            conn = prepare_experiment(exp_key)

            # 2. Release the connection so the controller has a clean slate.
            conn.disconnect()
            print("[Launcher] Disconnected from server.")

            # 3. Spawn the existing controller, passing its config file.
            #    Detached so it survives the launcher exiting.
            self._spawn_controller(cfg["controller_config"])

            # 4. Launcher's job is done — close the window / exit.
            print("[Launcher] Handoff complete. Exiting.")
            self.root.destroy()

        except Exception as e:
            self.status.config(text="Launch failed.")
            messagebox.showerror("Launch Error", str(e))

    def _spawn_controller(self, config_path):
        # the controller needs a console for its messages, which pythonw
        # (no console) would not give it
        python = sys.executable.replace("pythonw.exe", "python.exe")
        cmd = [python, CONTROLLER_SCRIPT, config_path]

        # Detach so the controller keeps running after the launcher exits.
        kwargs = {}
        if sys.platform == "win32":
            # its own console window (connection retries, tank errors, Ctrl+C)
            # in a new process group so it's fully independent.
            CREATE_NEW_CONSOLE = 0x00000010
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            kwargs["creationflags"] = CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP
            kwargs["close_fds"] = True

        subprocess.Popen(cmd, **kwargs)
        print(f"[Launcher] Spawned controller with config: {config_path}")


if __name__ == "__main__":
    root = tk.Tk()
    LauncherGUI(root)
    root.mainloop()
