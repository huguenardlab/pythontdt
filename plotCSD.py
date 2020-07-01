#Gabrielle code
#plot CSD.py 
#20200625
#Python display plot CSD for TDT 


#import of necessary library
import sys
import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from timeArray import *


def plotCSDdata(npdata,stimDelay,plotstructCSD):
          
    npdatab=np.squeeze(npdata)
    #ch=np.size(npdatab,axis=0)
    # calculate ch number, whether first time, or when replotting
    sp2=0.1*0.1 #100µm spacing between probe
    dyyl=-np.diff(np.diff(npdatab,axis=1),axis=1)/sp2
    ch=np.size(dyyl,axis=1)
    
    if not plotstructCSD[0]:  # if the first element of plotstructure is set, then replotting    
        #time array
      line=np.arange(16).tolist()  
      Fs=24414 #this assume sampling 
      results=timeTDT(npdatab,Fs)
      Si=results['Si']
      times=results['times']      


      stimdelay=0.006 #need to be extract from TDT
      postStimWait=0.002
      preStimDelay=0.001 
      postStimDisplay=0.03   
       
          
        #Plot
      
    #print (np.shape(npdata))    
      autoscalept1= int((stimdelay+postStimWait)/Si)
      autoscalept2=int((stimdelay+postStimDisplay)/Si)
      colormap=['red','blue','yellow','green','purple','white','cyan','magenta','orange','gold','skyblue','grey','seagreen','lavender','pink','turquoise']

    #print(autoscalept1)
    #print(autoscalept2)
      plt.style.use('dark_background')
      as1=np.amin(np.amin(dyyl[autoscalept1:autoscalept2,:]))
      as2=np.amax(np.amax(dyyl[autoscalept1:autoscalept2,:]))
    
      fig,ax=plt.subplots(ch,1, sharex=True,gridspec_kw={'hspace': 0})
      
      

      for i in range(ch):
        #line[i] = ax[i].plot(times, npdatab[i,:],colormap[i],linewidth=.5)
        line[i] = Line2D(times, dyyl[:,i],linewidth=.8,color=colormap[i])
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
      plotstructCSD[0]=True
      plotstructCSD[1]=line
      plotstructCSD[2]=fig
    else:
    # the following code should just replace y values and be very fast to draw
        for i in range(ch):
 
            plotstructCSD[1][i].set_ydata(dyyl[:,i])
            
        plotstructCSD[2].canvas.draw()
        plotstructCSD[2].canvas.flush_events()
    return plotstructCSD
