# TDT_controllerv12a.py

Version 12a of the TDT controller. It is based on `TDT_controllerv12.py`,
which is left unchanged. It adds a LogSteps option for the stim series, and
fixes problems in the loops that trigger stims and poll the TDT for data.

**Status:** compiles, but has not yet been run on the TDT hardware. Test it
in Preview Mode before using it for a real recording.

## How the controller works

Everything runs on the Tkinter event loop. There are no `while` loops or
threads. The TDT ActiveX objects (`TDevAcc.X`, `TTank.X`) are only called
from the main thread, and they should stay that way. Two timer loops
re-schedule themselves with `window.after`:

| Loop | Interval | Job |
|---|---|---|
| `clock()` | 1 s | Updates the time label while not recording. |
| `acquisLoop()` | 100 ms | Runs only while recording. **Trigger:** once the ISI has passed, calls `onestim()`, which sets the RZ5 tags and pulses `SingleStimTrigger`. **Poll:** while waiting for the TDT, reads the tank until the sweeps of the current stim are there, then reorders the channels, applies the baseline offset and plots. |

Two flags in `mainStruct` hand control back and forth between those two
steps:

- `waitingForTrigger`: waiting for the ISI to pass before the next stim.
- `waitingForTDT`: a stim was sent, waiting for its sweeps to appear in the
  tank.

## Changes from v12

### New option: LogSteps

A **LogSteps** checkbox in the main window (below Preview Mode) changes how
the stim values in a series are calculated. For stim n (n = 1, 2, 3...):

| LogSteps | Stim value | Example: initial 1 V, increment 0.5, 5 stims |
|---|---|---|
| off (default) | initial + (n-1) x increment | 1.0, 1.5, 2.0, 2.5, 3.0 V |
| on | initial x (1+increment)^(n-1) | 1.0, 1.5, 2.25, 3.38, 5.06 V |

With LogSteps on, the increment is a fraction (0.5 means each stim is 50%
bigger than the one before), not a voltage. The status label and the series
repeats work the same as before.

The setting is:
- read from the checkbox when Start is pressed (`mainStruct["logSteps"]`),
- saved and loaded with the parameter files (older files without it default
  to off),
- written to the tank notes, as `Stim increment (log steps, x(1+increment))`,
- recorded in the `numstim` column of the `TDTtrials` database table as a
  **negative** number: a LogSteps series of 5 stims is stored as `-5`, a
  linear one as `5`. Use `ABS(numstim)` for the number of stims and
  `numstim < 0` to find LogSteps trials.

  The negation happens only when the trial data is stored: only the copy of
  `mainStruct` handed to `addTrialData` gets the negative value
  (`numstim` is a plain signed `int`). `mainStruct["ns"]` stays positive for the run and the parameter
  files, and `micedbv5.py` (shared with the other controllers) is unchanged.

### Loop fixes

1. **Only one acquisition loop runs at a time.**
   v12 called `window.after(100, acquisLoop)` on every Start *and* Stop
   click, and the loop always re-scheduled itself. So every click added
   another loop, and they all polled the tank at once. In v12a,
   `startAcquisLoop()` cancels any waiting call (kept in the global
   `acquisJob`) before scheduling a new one. The loop also stops by itself
   when recording stops.

2. **Stop no longer finalizes the run twice.**
   In v12, pressing Stop during the ISI wait left `waitingForTrigger` set.
   When the ISI ran out, `onestim()` ran the end-of-run code a second time.
   That repeated `addTrialData` (the database entry), the `AppendNote` calls
   and the Trial # increment. Stop now clears both flags.

3. **Stop no longer leaves the poll running forever.**
   In v12, pressing Stop while waiting for data left `waitingForTDT` set. The
   expected sweep count could then never be reached, so the tank was read
   every 100 ms until the next Start. Fixed by the same flag clearing.

4. **The poll reads only the new sweeps.**
   v12 reopened the tank and ran `ParseEvV(0, N)` and `ParseEvInfoV(0, N, 6)`
   over *every* sweep in the block on every poll. That work grew with each
   stim and made the GUI slower as a run went on. v12a reads only the newest
   `nChan` sweeps with `ParseEvV(N-nChan, nChan)`, and only the first
   timestamp of each store (used for `stimDelay`).

5. **New sweep counting with a timeout.**
   v12 waited until the sweep count was *exactly*
   `((run-1)*ns + stim) * nChan`. If the tank ever held one sweep more or
   fewer than that, the run hung without any message. Missed triggers have
   not been a problem in practice (the 1-then-0 pulse on `SingleStimTrigger`
   is reliable), so the timeout is only a safeguard. v12a keeps
   `mainStruct["sweepCount"]`, the number of sweeps already read in the
   block, and treats the stim as done once `nChan` more have arrived. If they
   haven't arrived `tdtTimeout` seconds (10 s) after the trigger, the
   controller:
   - writes a message to the console and the log box,
   - resets `sweepCount` to what is actually in the tank,
   - moves on to the next stim.

   If the tank has *more* sweeps than expected, it prints a warning and uses
   the last `nChan`.

6. **Errors don't stop the loop.**
   In v12 the re-schedule was the last line of `acquisLoop`, so any error
   stopped acquisition for good (Tk only printed a traceback). In v12a the
   body is in `acquisStep()`, which `acquisLoop()` runs inside
   `try/except/finally`: the traceback is printed and the loop is always
   re-scheduled while recording.

7. **The clock keeps running between runs.**
   In v12, `clock()` stopped re-scheduling once recording started and nothing
   restarted it, so the time label froze after the first run. It now runs
   all the time and only updates the label when not recording.

8. **No more `time.sleep(1)` at Start.**
   The one-second wait after `SetSysMode` used to freeze the GUI. The rest of
   the Start setup now runs one second later in `startRun()`, scheduled with
   `window.after`. If Stop is pressed during that second, the start is
   cancelled.

### Other fixes

9. **The channel remap only applies to 16 channels.**
   The remap (keep channel 0, reverse channels 1-15) was hardcoded for 16
   channels but applied whenever `nChan > 1`. With 2 to 15 channels (for
   example the 4-channel store) it raised an `IndexError`. It now applies
   only when `nChan == 16`. Other channel counts keep the order TDT gives
   them.

10. **The Baseline Offset checkbox works.**
    v12 had `if baselineOffset.get:` with no `()`. That is always true, so the
    offset was applied whatever the checkbox said.

11. **Open File fixes.**
    - Cancelling the Open File dialog no longer crashes.
    - Loading a parameter file now also restores the train settings
      (`trainNP`, `trainFreq`), when the file has them.
    - Loading still only updates the menu, as in v12. `clickrecord` copies
      the menu values into `mainStruct` when a recording starts.

12. **No reconnect before every stim.**
    `onestim()` used to call `tdt.ConnectServer` and `ttank.ConnectServer`
    before each stim so it could reach `tdt` and `ttank`. That isn't needed:
    they are module-level globals, and a function can call their methods
    without a `global` statement (`global` is only needed to *assign* the
    name). The connection opened at startup is used for the whole session.
    If a connection ever drops during a run, a reconnect could go in an
    error handler instead.

### New settings and state

| Name | Where | Meaning |
|---|---|---|
| `tdtTimeout` | module constant, default `10` | Seconds to wait for the sweeps of one stim before skipping it. |
| `acquisJob` | global | Id of the waiting `window.after` call for `acquisLoop`, so it can be cancelled. |
| `mainStruct["sweepCount"]` | state | Sweeps already read in the current block. Reset to 0 at Start. |
| `mainStruct["tdtWaitStart"]` | state | Time the last stim was sent, used for the timeout. |
| `mainStruct["logSteps"]` | parameter | LogSteps checkbox, saved in parameter files. |

## Remaining issues

These were found while reviewing v12 but were not changed in v12a:

- **Plotting blocks the GUI.** `plotTDTdata` runs inside the loop, so the
  window can freeze briefly each time a sweep is plotted.

- **Late sweeps can be plotted for the wrong stim.** If a stim's sweeps
  arrive *after* the timeout, the next stim can see enough sweeps right away
  and plot those late sweeps instead of its own. Raise `tdtTimeout` if your
  sweeps can take longer than 10 s.

- **Every poll still asks for the whole block's event count.**
  `ReadEventsSimple('SSwp')` still counts every event in the block on each
  poll. Only copying the data into Python got cheaper. Reading with a time
  filter (`ReadEventsV` with a start time) would avoid this.

- **The remap for other channel counts is unknown.** If 4-channel (or other)
  recordings need a channel reorder, it has to be added next to the 16-channel
  one in `acquisStep()`.

- **Parameter files are read as text.** `readDict2` returns every value as a
  string, so at startup the values in `mainStruct` are strings until Start
  copies the menu values in. This works because the controller reads from the
  menu, but any new code that uses `mainStruct` values before Start must
  convert them first.

- **The increment label always says (V).** With LogSteps on, the increment
  is a fraction, but the label still reads "Stimulus Increment (V)".

- **Smaller leftovers:**
  - `mainStruct` has both `"thisstim"` and `"thisStim"` (only `"thisStim"`
    is used).
  - `"restart"` is set but never read.
  - The `newtankmessage` lines near the end of the window setup can never run.
  - Exiting during a recording does not put the TDT back in Idle mode
    (`SetSysMode(0)`).
