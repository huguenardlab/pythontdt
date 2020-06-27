#Gabrielle code 
#20200617
#Python display plot for TDT 

#import of necessary library
import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from matplotlib.lines import Line2D
from timeArray import *
from matplotlib.artist import Artist

data=loadmat ("Z:\\TDT\\Projects\\CNTNAP2\\20200612\\run-14\\matlab.mat")

npdata=data['aveDataPython']
npdatab=np.transpose(np.squeeze(npdata))
ch=np.size(npdatab,axis=1) 

line=np.arange(16).tolist()  
      
Fs=24414
results=timeTDT(npdatab,Fs)
Si=results['Si']
times=results['times']
      

stimdelay=0.006 #need to be extract from TDT
postStimWait=0.002
preStimDelay=0.001 
postStimDisplay=0.03 
endStim= int((0.005+0.001)/Si)  
                    
        
autoscalept1= int((stimdelay+postStimWait)/Si)
autoscalept2=int((stimdelay+postStimDisplay)/Si)
colormap=['red','blue','yellow','green','purple','white','cyan','magenta','orange','gold','skyblue','grey','seagreen','navy','pink','turquoise']
npdatab[int(0.005/Si):endStim,:]=0  #we want to blank the stim artifact 



    #print(autoscalept1)
    #print(autoscalept2)
plt.style.use('dark_background')
as1=np.amin(np.amin(npdatab[autoscalept1:autoscalept2,:]))
as2=np.amax(np.amax(npdatab[autoscalept1:autoscalept2,:]))
    
fig,ax=plt.subplots(ch,1, sharex=True,gridspec_kw={'hspace': 0})
      
for i in range(ch):
        #line[i] = ax[i].plot(times, npdatab[i,:],colormap[i],linewidth=.5)
        line[i] = Line2D(times, npdatab[:,i],linewidth=.8,color=colormap[i])
        #ax[i].plot(times, npdatab[i,:],colormap[i],linewidth=.5)
        ax[i].set_clip_on(False)
        ax[i].add_line(line[i])
        ax[i].set_ylim ((as1,as2))
        ax[i].set_xlim(((stimdelay-preStimDelay)*1000, times[autoscalept2]))
        #ax[i].set_clip_on(False)
        ax[i].axhline(y=0, color='black', linestyle='--',linewidth=.3)
        ax[i].yaxis.set_visible(False)
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[ch-1].set_xlabel ('Time (ms)')
        ax[i].set_clip_on(False)        
        #return line
fig.show() 
    
