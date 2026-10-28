# TDT experiment launcher

`launcher_gui.py` shows one button per experiment. Clicking one starts
OpenWorkbench (OpenEx) with that experiment's workspace, waits until the TDT
is ready, and then starts `TDT_controllerv13.py` with that experiment's
parameters file. The launcher window then closes, and the controller keeps
running in its own console window.

**Status:** compiles, but has not been run on the TDT computer. The
experiment list is a draft with placeholder values (see below), and two
assumptions about OpenWorkbench still need checking (see below).

## Running it

```
python launcher_gui.py
```

Run it from a normal console, or with `pythonw` to have no console for the
launcher itself. Its messages (prefixed with `[Launcher]`) show in that
console, and errors also show in a dialog box.

### Desktop icon

On the TDT computer, double-click **`make_desktop_shortcut.bat`** once. It
puts a **TDT Launcher** shortcut on the desktop (it finds the desktop even if
it is redirected to OneDrive). Double-clicking the shortcut runs
**`TDT_Launcher.bat`**, which starts `launcher_gui.py`.

- **Icon:** the shortcut uses the OpenWorkbench icon if OpenWorkbench is at
  `C:\TDT\OpenEx\OpenWorkbench.exe` (change `ICON` in
  `make_desktop_shortcut.bat` if not), otherwise the plain batch-file icon.
  To pick another one, right-click the shortcut > Properties > Change
  Icon.
- **Console window:** a console opens with the launcher and shows its
  `[Launcher]` messages, such as the connection attempts while the workspace
  loads. It closes when the launcher hands over to the controller. If the
  launcher crashes, the console stays open so the error can be read.
- **Moving the folder:** the shortcut points to `TDT_Launcher.bat` where it
  was when you made the shortcut. If the code folder moves, run
  `make_desktop_shortcut.bat` again from the new place.
- **Python on the PATH:** `TDT_Launcher.bat` runs the `python` found on the
  PATH. If it says "Python was not found", add Python to the PATH, or put
  the full path of `python.exe` in place of `python` in the batch file.

### Starting the controller without the launcher

The controller can still be started by itself, as before:

```
python TDT_controllerv13.py                  # loads recentv10.csv
python TDT_controllerv13.py neural_16ch      # loads z:/TDT/python_params/neural_16ch.csv
```

## What happens when you click an experiment

1. **Check the parameters file.** The experiment's `controller_config` must
   exist in `z:/TDT/python_params/`. This is checked first because otherwise
   the controller would exit at once and its console window would close
   before you could read why.
2. **Start OpenWorkbench** with the experiment's `.wsp` workspace
   (`ow_launcher.py`). If OpenWorkbench is already running, it is left alone
   and whatever workspace it has open is used. To load a different
   workspace, close OpenWorkbench first.
3. **Connect to the TDT** (`tdt_connection.py`). The launcher tries every 5
   seconds for up to 2 minutes, until the TDT reports a device, since the
   workspace takes a while to load:
   ```
   [Launcher] Attempt 1: no device yet (workspace still loading?), trying again in 5s
   ```
4. **Set the startup tags**, if the experiment has any (none for now). If a
   tag cannot be set, the launch stops with an error.
5. **Disconnect**, so the controller can make its own connection.
6. **Start the controller** in a new console window with the parameters
   file. The connection-retry messages, tank errors and Ctrl+C all work in
   that window. The controller still keeps running after the launcher
   closes.

The launcher does not change the TDT mode (Idle/Preview/Record). The
controller does that, as before.

## Files

| File | What it does |
|---|---|
| `launcher_gui.py` | The window with the experiment buttons; starts the controller |
| `launcher_app.py` | `prepare_experiment()`: steps 1 to 4 above |
| `experiment_config.py` | The list of experiments and the paths: **edit this one** |
| `ow_launcher.py` | Starts OpenWorkbench with a workspace |
| `tdt_connection.py` | `TDTConnection`: connect with retries, set tags, disconnect |
| `TDT_Launcher.bat` | Starts `launcher_gui.py`; the desktop shortcut runs it |
| `make_desktop_shortcut.bat` | Run once to put the TDT Launcher shortcut on the desktop |

These files use Python's usual snake_case names, while the controller uses
camelCase.

## Placeholders to fill in

Everything you need to edit is in `experiment_config.py`.

### 1. The experiments

The two entries, `neural_16ch` and `behavior_4ch`, are made up. Replace them
with your real experiments. Each entry looks like this:

```python
"neural_16ch": {
    "workspace": r"C:\TDT\Workspaces\neural_16ch.wsp",
    "device": "RZ5",
    "description": "16-channel neural recording",
    "startup_tags": {},
    "controller_config": "neural_16ch.csv",
},
```

| Field | What to put there |
|---|---|
| key (`"neural_16ch"`) | Any short name; it is only used inside the launcher |
| `workspace` | Full path of the OpenEx workspace (`.wsp`) for this experiment |
| `description` | The text on the button |
| `controller_config` | The controller's parameters file in `z:/TDT/python_params/`. A bare name like `neural_16ch.csv` is looked up there; `.csv` can be left off |
| `startup_tags` | Circuit tags to set before the controller starts, e.g. `{"RZ5.SomeTag": 1}`. Leave as `{}` if none (read assumption 2 below first) |
| `device` | Not used yet. It is set to `RZ5`, the device the controller sends its settings to. The first draft said `RZ2` |

**Making a parameters file.** Start the controller, set everything up for
that experiment (number of channels, stim settings, plot settings), and use
**Files → Save File** to save it in `z:/TDT/python_params/`. Use that file
name for `controller_config`. Files saved by v12c also work, because v13
translates the old key names when it loads them.

The window is 240 pixels high, which fits about three buttons. If you add
more experiments, make it taller in `launcher_gui.py`
(`self.root.geometry("360x240")`).

### 2. The OpenWorkbench path

```python
OPENWORKBENCH_EXE = r"C:\TDT\OpenEx\OpenWorkbench.exe"
```

Check that this is where OpenWorkbench is installed on the TDT computer. The
launcher stops with "OpenWorkbench not found" if it is not.

### 3. The parameters folder

```python
PARAMS_FOLDER = "z:/TDT/python_params/"
```

This must be the same folder as `paramsFolder` at the top of
`TDT_controllerv13.py`. If one changes, change the other.

## Assumptions to check on the TDT computer

### 1. OpenWorkbench opens a workspace given on its command line

The launcher runs `OpenWorkbench.exe <workspace.wsp>`, assuming it opens the
workspace the same way as double-clicking the `.wsp` file does. This has not
been checked.

**If it is wrong:** OpenWorkbench opens but no workspace loads, and after 2
minutes the launcher stops with:

```
Could not connect to OpenWorkbench after 120s: no device yet (workspace still loading?)
```

**The fix then** is to open the workspace through Windows instead
(`os.startfile(workspace)`, which is the same as double-clicking it), or
through OpenEx's own interface. Tell Claude what you see.

If a workspace just takes longer than 2 minutes to load, increase `timeout`
in `TDTConnection` (`tdt_connection.py`).

### 2. Startup tags can only be set once the circuit is loaded

OpenEx can usually only set a circuit tag when the circuit is running
(Standby, Preview or Record), not in Idle. The launcher leaves the TDT in
Idle, so a startup tag would likely fail with:

```
Could not set RZ5.SomeTag = 1
```

This does not matter now, since there are no startup tags, and the
controller sets all its stim tags itself at each stimulus. If you need a
startup tag later, the launcher will have to put the TDT in Standby first,
or the tag can be set by the controller after Start instead.

### 3. Other assumptions

- **TDevAcc's server name is `Local`**, as in the controller.
- **Only one OpenWorkbench runs at a time.** If one is already open, the
  launcher uses it as it is, even if it has a different workspace open. It
  prints a message saying so.
- **Python is the same one for both.** The controller is started with the
  same Python as the launcher (`python.exe` instead of `pythonw.exe`), so
  `pywin32` and `mysql-connector` must be installed in that Python.

## If something goes wrong

| What you see | Likely cause |
|---|---|
| "Controller parameters file not found" | `controller_config` is misspelled, or the file is not in `z:/TDT/python_params/` (is the Z: drive connected?) |
| "OpenWorkbench not found" / "Workspace not found" | Wrong path in `experiment_config.py` |
| "Could not connect to OpenWorkbench after 120s" | The workspace did not load (assumption 1), or it is slow (increase `timeout`) |
| "Could not set ..." | A startup tag is misspelled, or the TDT is in Idle (assumption 2) |
| The controller console prints "Attempt N: could not connect to Tank" | The TTank server is not ready yet. The controller keeps trying every 10 s; Ctrl+C gives up |
