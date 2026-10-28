# pythontdt

Python code for running slice electrophysiology experiments on the TDT
system (RZ5 with OpenEx). The controller sends the stimuli, reads each sweep
from the tank, plots the LFP and CSD online, writes notes to the tank, and
logs every trial in the lab database.

Started by JRH and GD in 06/2020.

## Quick start

Double-click **TDT Launcher** on the desktop and pick an experiment. The
launcher starts OpenWorkbench with that experiment's workspace, waits until
the TDT is ready, and opens the controller with that experiment's
settings. See `README_launcher.md`.

The controller can also be started by itself:

```
python TDT_controllerv13.py                  # the settings from the last Exit
python TDT_controllerv13.py neural_16ch      # z:/TDT/python_params/neural_16ch.csv
```

See `README_TDT_controllerv13.md`.

## Which file is current

| File | What it is |
|---|---|
| `TDT_controllerv13.py` | **The current controller** |
| `TDT_controllerv12c.py` | The previous controller, kept as the fallback until v13 is tested on the rig |
| `micedbv6.py` / `micedbv5.py` | Lab database access, for v13 / for v12c |
| `plotLFP_CSDv5.py` / `plotLFP_CSDv4.py` | Online LFP/CSD plots, for v13 / for v12c |
| `dblogin.py` | Connects to the lab database with the login in `db_login.ini` |
| `dict2file.py` | Reads and writes the parameter files |
| `offset_baseline.py` | Baseline offset of the sweeps (the Baseline Offset option) |
| `timeArray.py` | Time axis for the plots |
| `launcher_gui.py`, `launcher_app.py`, `experiment_config.py`, `ow_launcher.py`, `tdt_connection.py` | The experiment launcher |
| `TDT_Launcher.bat`, `make_desktop_shortcut.bat` | Start the launcher; put its icon on the desktop |

v13 and v12c need different versions of the database and plotting modules
because v13 renamed the parameter keys. Once v13 has been tested on the rig,
v12c, `micedbv5.py` and `plotLFP_CSDv4.py` move to `old/`.

The `README_*.md` files describe each version and what changed from the one
before.

## Setting up a computer

1. **Windows with TDT OpenEx** installed (TDevAcc and TTank come with it).
2. **Python** with these packages:
   ```
   pip install pywin32 mysql-connector-python numpy scipy matplotlib pandas
   ```
3. **Database login.** Copy `db_login_example.ini` to `db_login.ini` in this
   folder and fill in the password. `db_login.ini` is not in git, so the
   password never goes to GitHub. Without it the controller cannot list
   today's mice or save trials.
4. **The Z: drive** must be connected: the parameter files are in
   `z:/TDT/python_params/`.
5. **Desktop icon:** double-click `make_desktop_shortcut.bat` once.
6. **Experiments:** fill in `experiment_config.py` (see
   `README_launcher.md`).

## Where things are

| What | Where |
|---|---|
| Parameter files | `z:/TDT/python_params/` (`recentv10.csv` holds the settings from the last Exit of v13, `recentv9.csv` those of v12c) |
| Recorded data | The TDT tank, `D:/TDTdata/<project>/<date>`, one block per run |
| Trial records | Table `TDTtrials` in the lab database; the Mouse Menu lists the mice in `mousegeno` that are set for today or marked as Experimenting |
| Run notes | Written into the tank block at the end of each run, and shown in the text box at the bottom of the controller |

## Conventions

- **New versions are copies.** A change is made in a new file (v12c >
  v13), and the old version stays as it was until the new one has been
  tested. Each version has a README saying what changed.
- **Retired code goes to `old/`.** `old/` and `backup/` stay on the share
  but are not in git (see `.gitignore`).
- **Names.** The controller code uses camelCase. Tk variables end in `Var`,
  widgets in `Label`, `Entry`, `Btn` and so on. The launcher files use
  Python's usual snake_case.
- **Passwords** go in `db_login.ini`, never in the code.

## Status and to do

- [ ] Test v13 on the rig in Preview Mode, then with a recorded run.
- [ ] Test the launcher on the rig, and check its two assumptions (listed in
      `README_launcher.md`).
- [ ] Fill in the real experiments in `experiment_config.py`.
- [ ] Once v13 is tested: move v12c, `micedbv5.py`, `plotLFP_CSDv4.py` and
      the v12a/v12b/v12c READMEs to `old/`.
