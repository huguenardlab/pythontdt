import os

# DRAFT: the workspace paths and parameter files are placeholders until the
# real experiments are filled in.
# controller_config is a TDT_controllerv13 parameters file (.csv, as saved by
# its File > Save); a bare name is looked up in z:/TDT/python_params/
EXPERIMENTS = {
    "neural_16ch": {
        "workspace": r"C:\TDT\Workspaces\neural_16ch.wsp",
        "device": "RZ5",  # not used yet; the controller's tags are RZ5.*
        "description": "16-channel neural recording",
        "startup_tags": {},
        "controller_config": "neural_16ch.csv",
    },
    "behavior_4ch": {
        "workspace": r"C:\TDT\Workspaces\behavior_4ch.wsp",
        "device": "RZ5",
        "description": "4-channel behavioral recording",
        "startup_tags": {},
        "controller_config": "behavior_4ch.csv",
    },
}

# must match paramsFolder in the controller
PARAMS_FOLDER = "z:/TDT/python_params/"
OPENWORKBENCH_EXE = r"C:\TDT\OpenEx\OpenWorkbench.exe"
# full path, so the launcher works from any folder
CONTROLLER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "TDT_controllerv13.py")
