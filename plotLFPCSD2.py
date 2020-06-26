#Gabrielle code
#plot LFP CSD.py 
#20200617
#Python display plot for TDT 

#import of necessary library
import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.io import loadmat
from cycler import cycler

def plotTDTdata(npdata,stimDelay,plotstruct):
          
    npdatab=np.squeeze(npdata)
    ch=np.size(npdatab,axis=0)
    # calculate ch number, whether first time, or when replotting
    if not plotstruct[0]:  # if the first element of plotstructure is set, then replotting    
        #time array
      line=np.arange(16).tolist()  
      Fs=24414 #this assume sampling 
      Si=1/Fs
      nbpoints=np.size(npdata[:,1])
      time=np.arange(0,nbpoints,1)
      times=time*Si*1000        


      stimdelay=0.006 #need to be extract from TDT
      postStimWait=0.002
      preStimDelay=0.001 
      postStimDisplay=0.03   
       
          
        #Plot
      
    #print (np.shape(npdata))    
      autoscalept1= int((stimdelay+postStimWait)/Si)
      autoscalept2=int((stimdelay+postStimDisplay)/Si)
      colormap=['red','blue','yellow','green','purple','white','cyan','magenta','orange','gold','skyblue','grey','seagreen','navy','pink','turquoise']

    #print(autoscalept1)
    #print(autoscalept2)
      plt.style.use('dark_background')
      as1=np.amin(np.amin(npdatab[:,autoscalept1:autoscalept2]))
      as2=np.amax(np.amax(npdatab[:,autoscalept1:autoscalept2]))
    
      fig,ax=plt.subplots(ch,1, sharex=True,gridspec_kw={'hspace': 0})
      
      

      for i in range(ch):
        #line[i] = ax[i].plot(times, npdatab[i,:],colormap[i],linewidth=.5)
        line[i] = Line2D(times, npdatab[i,:],linewidth=.5,color=colormap[i])
        #ax[i].plot(times, npdatab[i,:],colormap[i],linewidth=.5)
        ax[i].add_line(line[i])
        ax[i].set_ylim ((as1,as2))
        ax[i].set_xlim(((stimdelay-preStimDelay)*1000, times[autoscalept2]))    
        ax[i].axhline(y=0, color='black', linestyle='--',linewidth=.3)
        ax[i].yaxis.set_visible(False)
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[ch-1].set_xlabel ('Time (ms)')
        
        #return line
      fig.show() 
      plotstruct[0]=True
      plotstruct[1]=line
      plotstruct[2]=fig
    else:
    # the following code should just replace y values and be very fast to draw
        for i in range(ch):
 
            plotstruct[1][i].set_ydata(npdatab[i,:])
            
        plotstruct[2].canvas.draw()
        plotstruct[2].canvas.flush_events()
    return plotstruct
