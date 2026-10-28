# TDT_controllerv13.py

Version 13 of the TDT controller. It is a copy of `TDT_controllerv12c.py`,
which is left unchanged as the fallback. It does the same experiments in the
same way: the changes are clearer names, renamed parameter keys, and a few
bug fixes. It uses `micedbv6.py` and `plotLFP_CSDv5.py`, the versions of the
database and plotting modules that take the new key names.

**Status:** compiles, but has not been run on the TDT hardware. Test it in
Preview Mode before using it for a real recording. Check in particular that
OK in the Mouse Menu sets the project in the main window, that a preview run
plots, and that a recorded run writes its trial to the database.

## Starting it

```
python TDT_controllerv13.py                  # loads the most recent settings
python TDT_controllerv13.py neural_16ch      # loads z:/TDT/python_params/neural_16ch.csv
```

The optional argument names a parameters file in `z:/TDT/python_params/`
(`.csv` can be left off; a full path also works). If the file does not
exist, the controller stops with "parameters file not found". Without an
argument it loads `recentv10.csv`, the settings saved at the last Exit.
The experiment launcher (`README_launcher.md`) starts the controller this
way.

Exit always saves the current settings to `recentv10.csv`, never to the
file named on the command line. To change that file, use
**Files > Save File**.

## Changes from v12c

### 1. Parameter keys renamed

The keys of `mainStruct`, which are also the names in the parameter files,
are now spelled consistently:

| Old key | New key |
|---|---|
| `nr` | `nRepeats` |
| `ns` | `nStims` |
| `isiT` | `isi` |
| `iniVal` | `initialStim` |
| `stepVal` | `stimStep` |
| `trainNP` | `trainPulses` |
| `thissweep` | `thisSweep` |
| `laststimtime` | `lastStimTime` |
| `tankfolder` | `tankFolder` |
| `oldmemo` / `allmemo` | `oldMemo` / `allMemo` |
| `1stMeasureBegin` / `1stMeasureEnd` | `measure1Begin` / `measure1End` |
| `2ndMeasureBegin` / `2ndMeasureEnd` | `measure2Begin` / `measure2End` |

The list is `renamedKeys` near the top of the file. Not renamed: the circuit
tags (`RZ5.trainNP` and the others) and the database column names.

**Older parameter files still load.** `readParams()` translates the old key
names when a file is read: the file named on the command line, the one
opened with Files > Open File, and the startup file.

**v13 has its own settings file**, `recentv10.csv` instead of v12c's
`recentv9.csv`, so v12c never reads a file with keys it does not know. The
first time v13 runs, `recentv10.csv` does not exist yet, so it starts from
`recentv9.csv`.

**Going back to v12c:** a parameters file saved with v13's Files > Save File
does not load in v12c, which does not know the new names.

**Keys missing from a file keep their defaults.** v12c replaced all of
`mainStruct` with the file it loaded; v13 only updates the keys the file
has.

### 2. Clearer names in the code

These do not change what the controller does.

- **Functions:** `clickrecord` > `onRecordClick`, `onestim` > `deliverStim`,
  `acquisLoop` / `acquisStep` > `acquisitionLoop` / `acquisitionStep`,
  `onClick` > `showWindow`, `updateMenu` > `applyParamsToGui`,
  `fileOpen` / `fileSave` > `openParamsFile` / `saveParamsFile`,
  `closeallFig` > `closeAllFigures`, `exitTDT` > `exitController`.
  `withdrawWindow` is split into `hideWindow` and `acceptMouseChoice` (OK in
  the Mouse Menu), since it did two different things.
- **Tk variables** end in `Var` and match their key: `initialStimVar`,
  `nStimsVar`, `trialVar` (was `exp`), `sliceVar` (was `slice2`),
  `projectVar` (was `prjt`), `channelAVar` (was `ch1`), and so on.
- **Widgets:** labels, entries and buttons that are never used again are
  created and placed in one line instead of getting names like `lbl2` or
  `txttf`. The ones the code does use again are named by what they are:
  `clockLabel`, `recordBtn`, `runStatusLabel`, `bipolarCheck`,
  `mouseCombo`, `projectCombo`.
- **Other:** `d` > `today`, `r` > `row`, `graphwindow` > `plotWindow`,
  `stimbuffer` > `logText`. Unused variables and old `#print` lines are
  removed.

The layout of the windows is the same as in v12c.

### 3. Bug fixes

- **Episode counter reset.** With `episodeTag` set, `startRun()` called
  `SetTargetVal(stimIndexReset,0)`, but `stimIndexReset` did not exist, so
  Start would have crashed. It now uses `episodeTag`. (`episodeTag` is empty
  by default, so this never ran.)
- **OK in the Mouse Menu.** The code that reads the mouse ID uses `re`,
  which was never imported. It only worked on older Pythons, where
  `from tkinter import *` happens to bring `re` along; on Python 3.10 and
  later OK would crash and the mouse ID would not be set. `re` is now
  imported.
- **No projects in the database.** OK in the Mouse Menu crashed if the
  database returned no projects, since the project list did not exist. It
  now skips the project.
- **Duplicate defaults.** `mainStruct` had both `thisstim` and `thisStim`,
  and both `thisSweep` and `thissweep`; the unused spellings and the unused
  `currentMouse` are removed.

### 4. Database login

`micedbv6.py` gets the database login from `db_login.ini` (through
`dblogin.py`) instead of having it typed in the code; see the main
`README.md`. `micedbv5.py`, used by v12c, does the same.

## Also in v12c

These were added to v12c on 10/28/2026, after its README was written, and
are in v13 too:

- **The parameters file on the command line**, described above.
- **The TDT connection retry works.** `connectTDT()` connects to the tank
  server again (that call had been commented out, so the tank could not be
  opened), uses the same `tdt` object as the rest of the program, and
  reports failures so the retry loop runs. It waits one second after
  connecting before asking for the device, and retries every
  `connectRetry` seconds (10). A COM error during the retry no longer stops
  it.

## Remaining issues

- The database queries are built by joining strings, so a memo containing
  a `'` breaks the insert. Passing the values to `cursor.execute` separately
  would fix that.
- The remaining issues listed in `README_TDT_controllerv12a.md` and
  `README_TDT_controllerv12b.md` still apply.
