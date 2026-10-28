# TDT_controllerv12c.py

Version 12c of the TDT controller. It is a copy of `TDT_controllerv12b.py`,
which is left unchanged, with two changes: Start no longer re-registers the
tank every time, and the startup keeps retrying the TDT connection instead of
quitting. Everything in `README_TDT_controllerv12b.md` and
`README_TDT_controllerv12a.md` still applies.

**Status:** compiles, but has not been run on the TDT hardware. Test it in
Preview Mode before using it for a real recording.

## Changes from v12b

### 1. The tank is registered only when the project changes

**The problem in v12b.** Every click on Start called `ttank.AddTank` (twice)
and `tdt.SetTankName` again, even though the tank folder
(`D:/TDTdata/<project>/<date>`) is the same for every run of the day.

**The fix.** That code is now in `registerTank()`. It remembers the tank it
registered (`registeredTank`) and only calls `AddTank` and `SetTankName`
again when the tank folder changes, that is, on the first Start and when you
switch to another project. `AddTank` is called once instead of twice. The
tank name is printed in the console and in the text box at the bottom of the
window when it is registered.

The tank cannot be registered when the program starts, because the project is
chosen in the Mouse Menu after that.

**What still happens on every Start.** Start still puts the TDT in Preview or
Record mode, and the end of each run puts it back in Idle. That is what makes
OpenEx start a new block for each run, which the notes, the database entry
and the sweep counting depend on, so it was not changed. Going from Idle to
Preview/Record restarts the circuit, and that is what resets the circuit's
counters, including the episode number shown in OpenEx. Registering the tank
had nothing to do with it. So with v12c the episode number still starts over
at each Start, as before.

**Optional explicit reset.** If you ever want to reset the episode number
yourself (for example if a future version stays in Record mode between
runs), set `episodeTag` near the top of the file to the circuit tag of the
counter, for example:

```python
episodeTag='RZ5.EpiCount'
```

`startRun()` then calls `tdt.SetTargetVal(episodeTag,0)` once the TDT is in
Preview/Record mode. The tag name above is only an example: use the name of
the tag in your RPvdsEx circuit. For `SetTargetVal` to work, the tag must be
a writable parameter tag; a counter that is only reset by a trigger input
needs a reset tag wired to that input instead. `episodeTag` is empty by
default, which does nothing.

### 2. The startup keeps retrying the TDT connection

**The problem in v12b.** If the tank server or Workbench/OpenEx was not
ready, or `ConnectServer` succeeded but no device was found ("TDT lied. We
were not actually connected"), the controller quit and had to be started
again by hand.

**The fix.** The three checks are now in `connectTDT()`. If any fails, the
controller prints which one, closes the partial connections, waits
`connectRetry` seconds (2 by default) and tries again, until the TDT reports
a device:

```
Attempt 1: TDT lied.  We were not actually connected, trying again in 2s
Attempt 2: TDT lied.  We were not actually connected, trying again in 2s
Device name #0 = RZ5
...
```

There is no limit on the number of attempts. Press **Ctrl+C** in the console
to give up. The GUI only opens once the connection is up.

Not retried: failing to import `pywin32` or to load the TDT driver
(`TDevAcc.ocx`). Waiting does not fix those, so they still quit right away.

`GetTargetSize('RZ5.StimBuffIn')` is now called after the device check
instead of before it.

## Smaller cleanups

- The `newtankmessage` lines that could never run (listed in the v12a
  README) are removed.
- `window.directoryname` and the unused `oldStimTime` are gone; the folder is
  a local variable in `registerTank()`.

## Remaining issues

The remaining issues listed in the v12a and v12b READMEs still apply.
