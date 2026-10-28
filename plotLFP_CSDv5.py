#Gabrielle code
#plot LFP CSD.py 
#20200617
#Python display plot for TDT
# v4: CSD traces are labeled by the LFP channel they are centered on
# (2..15 for 16 channels), and the y ticks follow the number of traces
# v5: uses the TDT_controllerv13 keys (thisSweep, lastStimTime, measure1Begin, ...)

import sys
import os
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from timeArray import *
mpl.rcParams['toolbar'] = 'None' 

channelsPlotStruct={
    "channelAFig":0,
    "channelBFig":0,
    "timeSeriesAFig":0,
    "timeSeriesAtData":0,
    "timeSeriesAyData":0,
    "timeSeriesBFig":0,
    "timeSeriesBtData":0,
    "timeSeriesByData":0
    }

def plotTDTdata(mainStruct):
  maxReps=5
  sp2=1
  for thisplot in range(2):  # we will loop through the code twice, once for lfp then for csd.
    npdatab=np.squeeze(mainStruct["thisSweep"])
    yoffset=mainStruct["gainLFP"] # gain for cortex -0.001, corpus callosum=-0.0001
    title="LFP, {0:.1f}mV separation".format(-yoffset*1000)
    plotyes=0 # not plotting!!!
    plotStruct=mainStruct["plotStructLFP"] 
    
    if mainStruct["doLFP"]:
       plotyes=1
    if thisplot==1 and mainStruct["doCSD"]: 
       plotStruct=mainStruct["plotStructCSD"]
       plotyes=1
       yoffset=mainStruct["gainCSD"] # gain for cortex -0.25, corpus callosum=-0.025
       title="CSD, {0:.1f}mV/mm^2 separation".format(-yoffset*1000)
       sp2=0.1*0.1 #100µm spacing between probe tips
       npdatab=-np.diff(np.diff(npdatab,axis=1),axis=1)/sp2
    if plotyes:
#        print("ndim "+repr(np.ndim(npdatab)))
#        print("size "+repr(npdatab.size))
        if np.ndim(npdatab)>1:
          ch=np.size(npdatab,axis=1)
        else:
          ch=1
#        print("chan "+repr(ch))
        ymax=-yoffset/2
        ymin=(ymax+yoffset*ch)
        plt.style.use('dark_background')
        stimdelay=mainStruct["stimDelay"]+.001 # need to correct for 1ms error in TDT/matlab
        Fs=24414
        results=timeTDT(npdatab,Fs)
        Si=results['Si']
        times=results['times'] # in ms
        displaypt1= int((stimdelay-mainStruct["preStimTime"]/1000)/Si)
        displaypt2=int((stimdelay+mainStruct["postStimTime"]/1000)/Si)
        artifactpt1=int(stimdelay/Si)
        stimDur=float(mainStruct["stimDur"])*2/1000/Si
        artifactpt2=int(stimdelay+stimDur)      
        npdatac=npdatab
        if np.ndim(npdatab)>1:
          npdatac[artifactpt1:artifactpt2,:]=np.nan
          npdatac=npdatac[displaypt1:displaypt2,:]
        else:
          npdatac[artifactpt1:artifactpt2]=np.nan
          npdatac=npdatac[displaypt1:displaypt2]
 
        results2=timeTDT(npdatac,Fs)
        times2=results2['times']-mainStruct["preStimTime"]
                
        # if the figure does not yet exist, then generate the axes.  otherwise use existing
        thisFig=plotStruct[2]        
        if mainStruct["restart"] or thisFig==0 or not plt.fignum_exists(thisFig.number):  # if the first element of plotstructure is set, then replotting    ########?? where we need to define this in the main code
          mainStruct["restart"]=0
          if thisplot==0:
            #print('reset all figs')
              # starting a new run, or deleting the LFP plot will cause all plots to close, a way of resetting
            plt.close('all')
            channelsPlotStruct["zeroTime"]=mainStruct["lastStimTime"]
          thisRep=1
          colormap=['red','blue','yellow','green','purple','white','cyan','magenta','orange','gold','skyblue','grey','seagreen','lavender','pink','turquoise']
          fig,ax=plt.subplots()
          ax.set_title(title)
          plt.rcParams['toolbar'] = 'None'
          plotoffset=yoffset
          mngr = plt.get_current_fig_manager()
          pos_string='+'+str(10+thisplot*405)+'+0'
          mngr.window.wm_geometry(pos_string)
          mngr.resize(width=400,height=600)
          currentoffset=0
          if ch>1:
            for i in range(ch):
              npdatac[:,i]=npdatac[:,i]+currentoffset
              currentoffset=currentoffset+plotoffset
          ax.plot(times2, npdatac) 
          ax.set_yticks(np.arange(ch)*plotoffset)
          first = 2 if thisplot==1 else 1   # CSD trace k is centered on LFP channel k+1
          ax.set_yticklabels(map(str, range(first, first+ch)))
          ax.set_clip_on(False) # turn off clipping        
          ax.spines['right'].set_visible(False)
          ax.spines['left'].set_visible(False)
          ax.spines['top'].set_visible(False)
          ax.set_xlabel ('Time (ms)')
          ax.set_ylabel ('Channels')
          ax.set_ylim(ymin,ymax)
          fig.show() 
          fig.set_clip_on(False)
          plotStruct[1]=ax
          plotStruct[2]=fig
          plotStruct[3]=plotoffset
          plotStruct[4]=1
          if thisplot==0:
             mainStruct["plotStructLFP"]=plotStruct
          else:
             mainStruct["plotStructCSD"]=plotStruct
        else: # figure already drawn, just plot onto it
            # now replotting on existing axes Figure 1, LFP , or in second time through loop, CSD, already exists
            plt.figure(plotStruct[2].number)  # pull up old figure
            thisRep=plotStruct[4]+1
            if thisRep>maxReps:
                thisRep=1
                ax=plotStruct[1]
                for artist in plt.gca().lines + plt.gca().collections:
                    artist.remove()
            plotoffset=plotStruct[3]
            currentoffset=0
            if ch>1:
              for i in range(ch):
                npdatac[:,i]=npdatac[:,i]+currentoffset
                currentoffset=currentoffset+plotoffset
            plotStruct[1].plot(times2, npdatac)
            plotStruct[2].canvas.draw()
            plotStruct[2].canvas.flush_events()
            plotStruct[4]=thisRep
            if thisplot==0:
                mainStruct["plotStructLFP"]=plotStruct
            else:
                mainStruct["plotStructCSD"]=plotStruct
            #now do other plots, single channels and time series
        if thisplot==1 and mainStruct["doCSD"]: # i.e. with CSD info, which is what we are using for time series
            elapsed=mainStruct["lastStimTime"]-channelsPlotStruct["zeroTime"]
            npdatad=np.squeeze(mainStruct["thisSweep"])
            npdatad=-np.diff(np.diff(npdatad,axis=1),axis=1)/sp2
            npdatad[artifactpt1:artifactpt2,:]=np.nan
            npdatad=npdatad[displaypt1:displaypt2,:]
            #print(npdatad)
            if mainStruct["plotChannelA"]:
                chAFig=channelsPlotStruct["channelAFig"]
                if chAFig==0 or not plt.fignum_exists(chAFig.number): # 3 is the single channel A plot
                    fig3=plt.figure(figsize=(4, 3))
                    channelsPlotStruct["channelAFig"]=fig3
                    if mainStruct["nChan"]>1:
                      thisData=npdatad[:,mainStruct["plotChannelA"]]
                    else:
                      thisData=npdatad
                    plt.plot(times2,thisData)
                    plt.plot([mainStruct["measure1Begin"],mainStruct["measure1End"]],[0,0],linewidth=4)
                    plt.ylim(yoffset,-yoffset)
                    fig3.show()
                    channelsPlotStruct["channelAFig"]=fig3
                    mngr = plt.get_current_fig_manager()
                    pos_string='+'+str(10)+'+700'
                    mngr.window.wm_geometry(pos_string)
                    mngr.resize(width=400,height=300)
                    plt.title('CSD A Channel {:d}'.format(mainStruct["plotChannelA"]+2))
                    ## need to put time bar in at time of measuring
                    plt.rcParams['toolbar'] = 'None'
                else:
                    plt.figure(chAFig.number)
                    plt.plot(times2,npdatad[:,mainStruct["plotChannelA"]])
                    chAFig.canvas.draw()
                    chAFig.canvas.flush_events()

                firstsample=int((mainStruct["measure1Begin"]+mainStruct["preStimTime"])/Si/1000)
                lastsample=int((mainStruct["measure1End"]+mainStruct["preStimTime"])/Si/1000)
                #print(firstsample,lastsample)
                snippet=npdatad[firstsample:lastsample,mainStruct["plotChannelA"]]
                meas=np.mean(snippet)
                chATSFig=channelsPlotStruct["timeSeriesAFig"]
                if chATSFig==0 or not plt.fignum_exists(chATSFig.number): # 3 is the single channel A plot
                    channelsPlotStruct["timeSeriesAtData"]=[0]
                    channelsPlotStruct["timeSeriesAyData"]=[meas]
                    fig3a=plt.figure(figsize=(4, 3))
                    mngr = plt.get_current_fig_manager()
                    pos_string='+'+str(10+405)+'+700'
                    mngr.window.wm_geometry(pos_string)
                    mngr.resize(width=400,height=300)

                    plt.plot(channelsPlotStruct["timeSeriesAtData"],channelsPlotStruct["timeSeriesAyData"],'o-')
                    fig3a.show()
                    plt.title('CSD A Channel {:d} Measure'.format(mainStruct["plotChannelA"]+2))
                    ## need to put time bar in at time of measuring
                    channelsPlotStruct["timeSeriesAFig"]=fig3a                    
                    plt.rcParams['toolbar'] = 'None'
                else:
                    channelsPlotStruct["timeSeriesAtData"]=np.append(channelsPlotStruct["timeSeriesAtData"],elapsed)
                    channelsPlotStruct["timeSeriesAyData"]=np.append(channelsPlotStruct["timeSeriesAyData"],meas)
                    plt.figure(chATSFig.number)
                    plt.plot(channelsPlotStruct["timeSeriesAtData"],channelsPlotStruct["timeSeriesAyData"],'o-')
                    chATSFig.canvas.draw()
                    chATSFig.canvas.flush_events()

            if mainStruct["plotChannelB"]:
                firstsample=int((mainStruct["measure2Begin"]+mainStruct["preStimTime"])/Si/1000)
                lastsample=int((mainStruct["measure2End"]+mainStruct["preStimTime"])/Si/1000)
                snippet=npdatad[firstsample:lastsample,mainStruct["plotChannelB"]]
                meas=np.mean(snippet)
                chBFig=channelsPlotStruct["channelBFig"]
                if chBFig==0 or not plt.fignum_exists(chBFig.number): # 3 is the single channel A plot
                   fig4=plt.figure(figsize=(4, 3))
                   channelsPlotStruct["channelBFig"]=fig4
                   plt.plot(times2,npdatad[:,mainStruct["plotChannelB"]])
                   plt.plot([mainStruct["measure2Begin"],mainStruct["measure2End"]],[0,0],linewidth=4)
                   plt.ylim(yoffset,-yoffset)
                   mngr = plt.get_current_fig_manager()
                   pos_string='+'+str(10+405*2)+'+700'
                   mngr.window.wm_geometry(pos_string)
                   mngr.resize(width=400,height=300)
                   fig4.show()
                   plt.title('CSD B Channel {:d}'.format(mainStruct["plotChannelB"]+2))
                   ## need to put time bar in at time of measuring
                   plt.rcParams['toolbar'] = 'None'
                else:
                    plt.figure(chBFig.number)
                    plt.plot(times2,npdatad[:,mainStruct["plotChannelB"]])
                    chBFig.canvas.draw()
                    chBFig.canvas.flush_events()
                chBTSFig=channelsPlotStruct["timeSeriesBFig"]
                if chBTSFig==0 or not plt.fignum_exists(chBTSFig.number): # 3 is the single channel A plot
                    channelsPlotStruct["timeSeriesBtData"]=[0]
                    channelsPlotStruct["timeSeriesByData"]=[meas]
                    fig4a=plt.figure(figsize=(4, 3))
                    plt.plot(channelsPlotStruct["timeSeriesBtData"],channelsPlotStruct["timeSeriesByData"],'o-')
                    fig4a.show()
                    mngr = plt.get_current_fig_manager()
                    pos_string='+'+str(10+405*3)+'+700'
                    mngr.window.wm_geometry(pos_string)
                    mngr.resize(width=400,height=300)
                    plt.title('CSD B Channel {:d} Measure'.format(mainStruct["plotChannelB"]+2))
                    channelsPlotStruct["timeSeriesBFig"]=fig4a
                    plt.rcParams['toolbar'] = 'None'
                else:    
                    channelsPlotStruct["timeSeriesBtData"]=np.append(channelsPlotStruct["timeSeriesBtData"],elapsed)
                    channelsPlotStruct["timeSeriesByData"]=np.append(channelsPlotStruct["timeSeriesByData"],meas)
                    plt.figure(chBTSFig.number)
                    plt.plot(channelsPlotStruct["timeSeriesBtData"],channelsPlotStruct["timeSeriesByData"],'o-')
                    chBTSFig.canvas.draw()
                    chBTSFig.canvas.flush_events()

                    
