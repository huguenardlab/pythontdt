import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt


    
def timeTDT(npdatab,Fs):
    d = dict();
    Si=1/Fs
    nbpoints=np.size(npdatab,axis=0)
    time=np.arange(0,nbpoints,1)
    times=time*Si*1000
    d['times']=times
    d['Si']=Si
    return  d
