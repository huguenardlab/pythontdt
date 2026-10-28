#Gabrielle 20200624

# Baseline offset 
#import of necessary library
import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

def offsetTDT(npdata):
    npdatab=npdata
    if np.shape(npdata)[1]>1:
        # only if we have more than one channel, and multiple sweeps
        # squeeze it down to one sweep
        # otherwise with single channel no need to squeeze.
        npdatab=np.squeeze(npdata)
    ch=np.size(npdata,axis=1)
    baselinePts=3
    numPointBaseline=int(np.size(npdatab,axis=0)*baselinePts/100)

    #print(ch)
    #print(baselinePts)

    #print(numPointBaseline)
    #@print(np.size(npdata))
    #print(np.size(npdatab))
    
    for i in range(ch):
        #print(i)
        #print(ch)
        #calculate mean voltage for first x (e.g. 100) pts
        baseline=np.mean(npdatab[1:numPointBaseline,i])
        #now offset by subtracting mean of first pts
        npdatab[:,i]=npdatab[:,i]-baseline
    return npdatab 
