import os
import subprocess

from experiment_config import OPENWORKBENCH_EXE

OPENWORKBENCH_IMAGE = os.path.basename(OPENWORKBENCH_EXE)


def is_openworkbench_running():
    """True if an OpenWorkbench process is already running."""
    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {OPENWORKBENCH_IMAGE}", "/NH"],
        capture_output=True, text=True)
    return OPENWORKBENCH_IMAGE.lower() in result.stdout.lower()


def launch_openworkbench(workspace):
    """
    Start OpenWorkbench with the given workspace (.wsp) and return without
    waiting; TDTConnection.connect() waits until the workspace is loaded.
    If OpenWorkbench is already running it is left alone, since a second
    copy cannot serve the same TDevAcc connection.
    """
    if not os.path.isfile(OPENWORKBENCH_EXE):
        raise FileNotFoundError(f"OpenWorkbench not found: {OPENWORKBENCH_EXE}")
    if not os.path.isfile(workspace):
        raise FileNotFoundError(f"Workspace not found: {workspace}")

    if is_openworkbench_running():
        print("[Launcher] OpenWorkbench is already running; using the open "
              "workspace (close it first to load a different one).")
        return

    subprocess.Popen([OPENWORKBENCH_EXE, workspace])
    print(f"[Launcher] Started OpenWorkbench with {workspace}")
