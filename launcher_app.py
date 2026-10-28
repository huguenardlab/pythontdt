import os

from experiment_config import EXPERIMENTS, PARAMS_FOLDER
from ow_launcher import launch_openworkbench
from tdt_connection import TDTConnection


def prepare_experiment(exp_key):
    """
    Startup preparation only:
      1. Launch OpenWorkbench with the workspace
      2. Connect via TDevAcc
      3. Apply one-time startup tags
    Does NOT set acquisition mode — the controller handles that.
    Returns the connection so the caller can close it before handoff.
    """
    cfg = EXPERIMENTS[exp_key]
    print(f"[Launcher] Preparing: {cfg['description']}")

    # check the controller's parameters file now: if it is missing the
    # controller exits at once and its console closes before it can be read
    params_path = os.path.join(PARAMS_FOLDER, cfg["controller_config"])
    if not params_path.lower().endswith(".csv"):
        params_path += ".csv"
    if not os.path.isfile(params_path):
        raise FileNotFoundError(f"Controller parameters file not found: {params_path}")

    launch_openworkbench(cfg["workspace"])

    conn = TDTConnection()
    conn.connect()
    print("[Launcher] Connected to OpenEx server.")

    for tag_path, value in cfg.get("startup_tags", {}).items():
        conn.set_tag(tag_path, value)
        print(f"[Launcher] Set {tag_path} = {value}")

    return conn
