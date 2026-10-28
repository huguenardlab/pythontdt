# TDT_controllerv12b.py

Version 12b of the TDT controller. It is a copy of `TDT_controllerv12a.py`,
which is left unchanged, with two changes: the Stop button responds right
away, and the controller uses `plotLFP_CSDv4.py` for plotting. Everything in
`README_TDT_controllerv12a.md` still applies, apart from the corrections at
the end of this file.

**Status:** compiles, but has not been run on the TDT hardware. Test it in
Preview Mode before using it for a real recording.

## Changes from v12a

### 1. Stop responds right away, and extra clicks cannot restart a recording

**The problem in v12a.** Clicking Stop set the button text to "Start" and
then finalized the run in the same click handler: `SetSysMode(0)`, opening
the tank, the `addTrialData` database entry and the `AppendNote` calls. Tk
only redraws the window after the handler returns, so the button kept
showing "Stop" and the GUI was frozen until all of that finished. Clicks
made during the freeze were not lost: Tk queued them and ran them once the
handler returned. By then the recording was stopped, so a second click on
"Stop" started a **new recording**.

The same could happen when a run ended by itself: the button showed "Stop"
during the end-of-run work, and a click in that time also started a new
recording.

**The fix.** The end-of-run code is now in its own function, `finishRun()`.
When `onestim()` reaches the end of the run (after Stop, or when all runs are
done), it:

1. sets the button text to **"Stopping..."** and disables the button,
2. calls `window.update_idletasks()`, so the new text is drawn **before**
   the slow work starts,
3. runs `finishRun()`,
4. sets `mainStruct["recording"]` to 0, even if `finishRun()` raised an
   error,
5. re-enables the button and sets it back to "Start" 500 ms later
   (`enableRecordButton()`).

Clicks made while the GUI is busy still get queued, but Tk handles them
before the 500 ms timer runs, while the button is still disabled, so they
are dropped. Step 4 and the `try/finally` mean an error in the end-of-run
code cannot leave the button disabled or the controller stuck in recording
mode.

What the end-of-run code does is unchanged: the same tank notes, database
entry and Trial # increment as in v12a. The only change to `clickrecord()`
is that the Stop branch no longer sets the button text itself.

| Button text | Meaning |
|---|---|
| Start | Idle. Click to start a recording. |
| Stop | Recording. Click to stop. |
| Stopping... (greyed out) | Finalizing the run. Clicks are ignored. |

### 2. Uses plotLFP_CSDv4

The import is now `from plotLFP_CSDv4 import *` instead of `plotLFP_CSDv3`.
In v4, CSD traces are labeled by the LFP channel they are centered on (2 to
15 for 16 channels), and the Plot A/B titles use the same numbers. See
`README_plotLFP_CSDv4.md`. What you type for Meas. A and Meas. B in the
Plot Menu has not changed.

## Corrections to README_TDT_controllerv12a.md

- **`"restart"` is used.** The v12a README says `mainStruct["restart"]` is
  set but never read. That is wrong: the plotting module reads it on the
  first plot after a Stop, closes all figures and resets the time series for
  the new run.

## Remaining issues

The remaining issues listed in the v12a README still apply. One more was
found while making v12b, and was not changed:

- **Stop during the first second after Start finalizes an empty run.**
  Start sets `recording` right away, but the run only begins one second
  later in `startRun()`. If Stop is clicked in that second, `startRun()` is
  cancelled as intended, but `onestim()` still runs the end-of-run code. It
  writes tank notes, and outside Preview Mode a database entry, for a run
  that recorded nothing, using the block of the previous run.
