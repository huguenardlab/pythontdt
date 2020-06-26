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
    npdatab=np.squeeze(npdata)
    ch=np.size(npdata,axis=1)
    
    baselinePts=3
    numPointBaseline=int(np.size(npdatab,axis=0)*baselinePts/100)

#numPointBaseline=np.size(npdatab[1])*baselinePts/100

    #if baselineOffset:

    for i in range(ch):
#calculate mean voltage for first x (e.g. 100) pts
        baseline=np.mean(npdatab[1:numPointBaseline,i])
#now offset by subtracting mean of first pts
        npdatab[:,i]=npdatab[:,i]-baseline
    return npdatab 