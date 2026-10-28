# plotLFP_CSDv4.py

Version 4 of the online LFP/CSD plotting module. It is a copy of
`plotLFP_CSDv3.py`, which is left unchanged. Only the channel labels change;
the data, the CSD calculation and the measurements are the same as in v3.

**Status:** compiles, but has not been run with the TDT yet.

## Using it

The controllers still import v3. To use v4, change the import in the
controller (for example `TDT_controllerv12a.py`):

```python
from plotLFP_CSDv4 import *
```

## Changes from v3

### CSD traces are labeled by the LFP channel they are centered on

The CSD is the second spatial difference of the LFP, so it has two fewer
traces than there are channels (14 for a 16 channel probe). CSD trace k
(0-based) uses LFP channels k, k+1 and k+2, so it is centered on LFP channel
k+1.

In v3, the CSD figure was labeled 1 to 16, like the LFP figure, so the
labels did not match the channel depths. In v4, the CSD traces are labeled
with the 1-based LFP channel at their center:

| Figure | v3 y labels | v4 y labels (16 channels) |
|---|---|---|
| LFP | 1..16 | 1..16 |
| CSD | 1..16 | 2..15 |

The same number now means the same depth in both figures. The missing 1 and
16 in the CSD figure are the two end channels that the CSD loses.

### The y ticks follow the number of traces

v3 always drew 16 ticks, whatever the number of channels. v4 draws one tick
per trace (`np.arange(ch)*plotoffset`), so the ticks are right for the 14
CSD traces and for probes that do not have 16 channels.

### Plot A and B titles use the same numbering

The titles of the single channel and measure plots (`CSD A Channel n`,
`CSD A Channel n Measure`, and the B versions) now show `plotChannelA+2`
(or `plotChannelB+2`), which is the number of that trace on the CSD figure's
y axis.

**What you type in the Plot Menu has not changed.** Meas. A and Meas. B are
still the 0-based CSD trace index, so typing 13 gives the trace labeled 15
on the CSD figure, and the title says `CSD A Channel 15`. The valid values
are still 1 to 13 for 16 channels: 0 turns the plot off, and 14 or 15 are
past the last CSD trace.
