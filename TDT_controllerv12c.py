# TDT_controller v 11  will do both CSD/LFP and MUA
# and version 12 will do stimulus trains
# version 12a: only one acquisition loop runs at a time, Stop clears the
# trigger/TDT wait flags, the poll reads only the newest sweeps and gives up
# after tdtTimeout seconds, and an error no longer kills the loop
# LogSteps option: stim n is initial*(1+increment)^(n-1) instead of
# initial+(n-1)*increment
# version 12b: the Start/Stop button shows "Stopping..." and is disabled while
# the run is finalized, so extra clicks cannot start a new recording; uses
# plotLFP_CSDv4 (CSD traces labeled by their center LFP channel)
# version 12c: the tank is registered only when the project changes instead of
# on every Start, Start can reset the episode counter (episodeTag), and the
# startup keeps retrying the TDT connection every connectRetry seconds;
# an optional command line argument names a parameters file in paramsFolder
# to load instead of the most recent one
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import Text
from tkinter import *
from micedbv5 import *
from tkinter import ttk
from offset_baseline import *
from plotLFP_CSDv4 import *
from dict2file import *
import tkinter as tk
import sys
import os
import shutil
import time
import threading
import collections
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
#global mainStruct
import datetime
import traceback
from datetime import timedelta
paramsFolder='z:/TDT/python_params/'
ParamsVersion='9'
tdtTimeout=10 # seconds to wait for the sweeps of one stim before giving up
acquisJob=None # id of the pending window.after call for acquisLoop
connectRetry=10 # seconds between attempts to connect to the TDT at startup
# circuit tag of the episode counter shown in OpenEx, set to 0 on each Start;
# leave empty to rely on the Idle->Preview/Record mode change to reset it
episodeTag=''
registeredTank=None # tank folder already registered with AddTank/SetTankName
mainStruct= { 
  "baselineOffset": False,  
  "stimDur":0.1,
  "thisstim":0,
  "preStimTime": 1,
  "postStimTime": 5,
  "plotChannelA": 13,
  "plotChannelB": 0,
  "1stMeasureBegin": 3,
  "1stMeasureEnd": 3.5,
  "2ndMeasureBegin": 2,
  "2ndMeasureEnd": 3,
  "gainLFP":-0.0005,
  "gainCSD":-0.025,
  "doLFP": True,
  "doCSD": True,
  "doMUA": False,
  "currentMouse": 0,
  "stimDelay": 0,
  "thisSweep": 0,
  "plotStructLFP":[0,0,0,0,0,0],
  "plotStructCSD":[0,0,0,0,0,0],
  "restart":0,
    "run":0,
    "recording":0,
    "stim":0,
    "isiT":15,
    "iniVal":1,
    "stepVal":1,
    "nr":8,
    "ns":1,
    "laststimtime":0,
    "project":0,
    "slice":0,
    "block":0,
    "curRun":0,
    "curStim":0,
    "thissweep":0,
    "mouseID":0,
    "tankfolder":0,
    "nChan":16,
    "waitingForTrigger":0,
    "waitingForTDT":0,
    "oldmemo":'',
    "allmemo":'',
    "trainNP":1,
    "trainFreq":100,
    "logSteps":False,
    "sweepCount":0,
    "tdtWaitStart":0
}
# here is where you go when you click start
def clickrecord():
    print("click record")
#    if mainStruct["doMUA"]:
#        mainStruct["nChan"]=1
    if mainStruct["recording"] :
     mainStruct["recording"]=0
     # onestim() shows "Stopping..." and sets the button back to Start
     # once the run is finalized
     mainStruct["run"]=1000
     mainStruct["stim"]=1000
     mainStruct["restart"]=1
     # clear the wait flags so acquisLoop cannot trigger onestim again
     # (which would finalize the run a second time) or keep polling the tank
     mainStruct["waitingForTrigger"]=0
     mainStruct["waitingForTDT"]=0
     if mainStruct["nChan"]<3:
       mainStruct["doCSD"]=0
       # cannot do CSD if there are less than 3 channels
     onestim()
    else:
        record['text']= "Stop"
        mainStruct["laststimtime"]=time.time()-10000
        mainStruct["waitingForTrigger"]=1
        registerTank()
        rslt=tdt.SetTargetVal('RZ5.BipolarStim',Bipolar.get())
        #print(rslt)
        tdt.SetTargetVal('RZ5.StimDuration',stimdur.get())
        mainStruct["recording"]=1
        if PreviewMode.get():
            mode=2
        else:
            mode=3
        tdt.SetSysMode(mode)
        # give TDT a second to change mode without freezing the GUI
        window.after(1000,startRun)

# register today's tank for the current project with TTank and the TDT; this
# only has to be done again when the project (and so the tank folder) changes
def registerTank():
    global registeredTank
    thisProject=prjt.get()
    # if user fails to specify project it will use the TEST project
    if thisProject=='':
      thisProject='TEST'
      prjt.set(thisProject)
    directoryname='D:/TDTdata/'+thisProject
    tankfolder=directoryname.replace('/','\\')+'\\'+d
    mainStruct["tankfolder"]=tankfolder
    if tankfolder==registeredTank:
        return
    NewTank=ttank.AddTank(d,'REGISTER@'+directoryname)
    if NewTank:
       print('New Tank Added: '+directoryname)
    else:
        print('ERROR! New Tank '+directoryname+' was not added.')
        window.destroy()
        sys.exit()
    NewTankName=tdt.SetTankName(tankfolder)
    #print(NewTankName)
    if NewTankName:
        print('New Tank Name: '+tankfolder)
    else:
        print('ERROR! Could not name new tank '+tankfolder)
        window.destroy()
        sys.exit()
    registeredTank=tankfolder
    stimbuffer.insert(INSERT,'\nTank: '+tankfolder)

def startRun():
        if not mainStruct["recording"]:
            return # Stop was pressed during the one second wait
        if episodeTag:
            # start the episode count displayed in OpenEx from 0 for this run
            tdt.SetTargetVal(stimIndexReset,0)
#        mainStruct["doMUA"]=MUAMode.get()
        mainStruct["nr"]=nrep.get()
        mainStruct["ns"]=nstim.get()
        mainStruct["stimDur"]=stimdur.get()
        mainStruct["iniVal"]=initv.get()
        mainStruct["stepVal"]=stepv.get()
        mainStruct["logSteps"]=LogSteps.get()
        mainStruct["isiT"]=isi.get()
        mainStruct["bipolar"]=Bipolar.get()
        mainStruct["trainNP"]=trainNP.get()
        mainStruct["trainFreq"]=trainFreq.get()
        mainStruct["nChan"]=numChans.get()        
        mainStruct["run"]=1
        mainStruct["stim"]=0
        rslt=ttank.OpenTank(d,'R')
        mainStruct["oldmemo"]=memo.get()
        mainStruct["block"]=ttank.GetHotBlock()
        mainStruct["sweepCount"]=0 # new block, no sweeps read yet
        mainStruct["waitingForTDT"]=0
        startAcquisLoop()

# schedule acquisLoop, cancelling any pending call first so that only one
# loop is ever running
def startAcquisLoop():
    global acquisJob
    if acquisJob is not None:
        window.after_cancel(acquisJob)
    acquisJob=window.after(100,acquisLoop)

def clock():
    # acquisLoop updates the label while recording
    if mainStruct["recording"]<1:
        t=time.strftime('%I:%M:%S %p',time.localtime())+'{: 4.0f}'.format(time.time()-mainStruct["laststimtime"])
        lblt.config(text=t)
    window.after(1000,clock)

def onClick(a):
 a.deiconify()
       
def withdrawWindow(a):
       if a.title()=="Mouse choice":
           mouseInfo=mouseList.get()
           project=projectList.get() # get project from mouse window #mouseInfo.partition(' Strain:')
           prjt.set(project) # and set it to main window
           mainStruct["project"]=project # and in mainstruct
           id=re.findall('eartag:(.*) p',mouseInfo)
           if id:
               mouseID=id[0]
           else:
               mouseID=0
           mainStruct["mouseID"]=mouseID
       a.withdraw()

#Close all figure
def closeallFig():
    plt.close('all')
    
#Exit TDT properly
def exitTDT():
    print ('Exit has been pressed')
    tankCheck=ttank.CheckTank(d)
    ttank.CloseTank()
    tdt.CloseConnection()
    ttank.ReleaseServer()
    window.destroy()
    mouseWindow.destroy()
    graphwindow.destroy()
    fileWindow.destroy()
    root.destroy()
    writeDict(fullParamsPath,mainStruct)
    closeallFig()
    sys.exit()
    

#trigger the stim, create and store Notes
def acquisLoop():
    global acquisJob
    acquisJob=None
    try:
        acquisStep()
    except Exception:
        # print the error but keep the loop alive
        traceback.print_exc()
    finally:
        # only one loop: it stops when recording stops and clickrecord
        # starts it again through startAcquisLoop
        if mainStruct["recording"] and acquisJob is None:
            acquisJob=window.after(100,acquisLoop)

def acquisStep():
    timeLeft=mainStruct["laststimtime"]+mainStruct["isiT"]-time.time()
    #print(timeLeft)
    t=time.strftime('%I:%M:%S %p',time.localtime())
    if mainStruct["recording"]:
        t=t+': Next Stim in '+'{:4.1f}s'.format(timeLeft)
        if t!='':
          lblt.config(text=t)                        
        newmemo=memo.get()
    if mainStruct["waitingForTrigger"]:
        thistime=time.time()
        if thistime-mainStruct["laststimtime"]>mainStruct["isiT"]:
            mainStruct["waitingForTrigger"]=0
            onestim()
    if mainStruct["waitingForTDT"]:
        nChan=int(mainStruct["nChan"])
        # check the timeout first so it still fires if the tank reads fail
        timedOut=time.time()-mainStruct["tdtWaitStart"]>tdtTimeout
        rslt=ttank.OpenTank(d,'R')#do it only first time
        #print("Open Tank Result"+repr(rslt))
        mainStruct["block"]=ttank.GetHotBlock()
        rslt=ttank.SelectBlock(mainStruct["block"])
        #print("Select Block Result"+repr(rslt))
        # sweepCount is the number of sweeps already read in this block, so
        # the stim is done when nChan more have arrived
        expectedsweeps=mainStruct["sweepCount"]+nChan
        #print("expected sweeps = "+repr(expectedsweeps))
        N = ttank.ReadEventsSimple('SSwp')
        #print("ReadEventsSimple SSwp Result "+repr(N))
        if N<expectedsweeps:
            if timedOut:
                msg='No data from TDT after {:d}s ({:d} of {:d} sweeps), skipping Run {:s} Stim {:s}'.format(tdtTimeout,N-mainStruct["sweepCount"],nChan,mainStruct["curRun"],mainStruct["curStim"])
                print(msg)
                stimbuffer.insert(INSERT,'\n'+msg)
                # resynchronize on what is in the tank and go on to the next stim
                mainStruct["sweepCount"]=N
                mainStruct["waitingForTDT"]=0
                mainStruct["waitingForTrigger"]=1
            return
        if N>expectedsweeps:
            print('Warning: expected {:d} sweeps, tank has {:d}, using the last {:d}'.format(expectedsweeps,N,nChan))
        # read only the sweeps of this stim instead of the whole block
        data = ttank.ParseEvV(N-nChan, nChan)
        npdata = np.array(data)
        if np.ndim(npdata)==1:
            npdata=npdata.reshape(-1,1)
        # stimDelay uses the first sweep and first stim of the block
        timeStamps=ttank.ParseEvInfoV(0,1,6)
        #print(timeStamps)
        E = ttank.ReadEventsSimple('EpcV')
        #print("ReadEventsSimple EpcV Result"+repr(E))
        stimStamps=ttank.ParseEvInfoV(0,1,6)
        if stimStamps is None:
            # for some reason TDT is not reading out stimStamps reliably
            # with this new controller #11, so setting the delay to
            # what is should be for the block_store_1_4Ch, which is 400 ms
            stimStamps=(timeStamps[0]+.4,)
        #print(stimStamps)
        if nChan==16:
            # 16 channel probe mapping: keep channel 0, reverse 1..15
            newrange=range(15,0,-1)
            newrange=np.insert(newrange,0,0)
            #print(newrange)
            mainStruct["thissweep"]=npdata[:,newrange]
        else:
            mainStruct["thissweep"]=npdata
        mainStruct["sweepCount"]=N
        mainStruct["waitingForTDT"]=0
        mainStruct["waitingForTrigger"]=1
        #Calculus of the Stimdelay here because it needs to wait to have data in the time/ stim Stamps 
        mainStruct["stimDelay"]=stimStamps[0]-timeStamps[0]
        if baselineOffset.get():
            mainStruct["thissweep"]=offsetTDT(mainStruct["thissweep"])
        if plotModeLFP.get() or plotModeCSD.get():
            mainStruct["plotChannelA"]=ch1.get()
            mainStruct["plotChannelB"]=ch2.get()
            mainStruct["1stMeasureBegin"]=start1.get()
            mainStruct["1stMeasureEnd"]=end1.get()
            mainStruct["2ndMeasureBegin"]=start2.get()
            mainStruct["2ndMeasureEnd"]=end2.get() 
            mainStruct["gainLFP"]=gainLFP.get()
            mainStruct["gainCSD"]=gainCSD.get()
            mainStruct["doLFP"]=plotModeLFP.get()
            mainStruct["doCSD"]=plotModeCSD.get()
            mainStruct["preStimTime"]=preStimDisplay.get()
            mainStruct["postStimTime"]=postStimDisplay.get()
            plotTDTdata(mainStruct)

def onestim() :
    if mainStruct["run"]<=mainStruct["nr"] :
      if mainStruct["stim"]<mainStruct["ns"] :
        mainStruct["stim"]+=1
        if mainStruct["logSteps"]:
            # log steps: each stim is (1+increment) times the one before
            mainStruct["thisStim"]=mainStruct["iniVal"]*(1+mainStruct["stepVal"])**(mainStruct["stim"]-1)
        else:
            mainStruct["thisStim"]=mainStruct["iniVal"]+ (mainStruct["stim"]-1)*mainStruct["stepVal"]
        lblrunstatus.config(text='Run '+str(mainStruct["run"])+' Stim '+str(mainStruct["stim"])+'{: .1f}'.format(mainStruct["thisStim"])+'V')
        mainStruct["curRun"]=str(mainStruct["run"])
        mainStruct["curStim"]=str(mainStruct["stim"])
        #print("oneStim")
        # send out current stimulus va
        tdt.SetTargetVal('RZ5.SingleStimValue',mainStruct["thisStim"])
        tdt.SetTargetVal('RZ5.StimEnable',1)
        
        tdt.SetTargetVal('RZ5.StimIndex',mainStruct["stim"])
        tdt.SetTargetVal('RZ5.StimDuration',stimdur.get())
        tdt.SetTargetVal('RZ5.BipolarStim',Bipolar.get())
        tdt.SetTargetVal('RZ5.trainNP',trainNP.get())
        tdt.SetTargetVal('RZ5.trainInterval',(1000/trainFreq.get())-.1)
        # trigger a sweep with a rising edge signal
        tdt.SetTargetVal('RZ5.SingleStimTrigger',1)
        # reset SingleStimTrigger value to 0, so that it can be triggered next time
        # the assumption is that the trigger has actually already been detected.
        tdt.SetTargetVal('RZ5.SingleStimTrigger',0)
        mainStruct["laststimtime"]=time.time()
        mainStruct["waitingForTDT"]=1;
        mainStruct["tdtWaitStart"]=time.time()
        newmemo=memo.get()
        if newmemo!=mainStruct["oldmemo"]:
            mainStruct["oldmemo"]=newmemo
            mainStruct["allmemo"]=mainStruct["allmemo"]+" [Run #" + str(mainStruct["run"])+ ", Changed Condition:" +newmemo + " at " +time.strftime('%I:%M:%S %p',time.localtime())+"]"
      else :
        mainStruct["run"]+=1
        mainStruct["stim"]=0
        onestim()
    else :
        # DONE WITH STIMS AND RUNS
        # show the stop and disable the button before the slow end-of-run
        # work, so clicks made during it are ignored instead of being queued
        # and starting a new recording
        record['text']= "Stopping..."
        record.state(['disabled'])
        window.update_idletasks()
        try:
            finishRun()
        finally:
            mainStruct["recording"]=0
            # re-enable later, so the clicks queued while the GUI was busy
            # reach a disabled button and are dropped
            window.after(500,enableRecordButton)

# end of run: put the TDT in Idle, write the tank notes and the database entry
def finishRun():
    tdt.SetSysMode(0)
    rslt=99
    rslt=ttank.OpenTank(mainStruct['tankfolder'],'R')
    #print('open tank for final read',rslt,d)
    rslt=ttank.OpenTank(d,'R')
    #print('open tank for final read',rslt,d)
    ttsb=ttank.SelectBlock(mainStruct["block"])
    #print('t tank name, and select result',mainStruct["block"],ttsb)
    project='Project: '+prjt.get()
    memoNote='Memo: '+ memo.get()
    mouseNb='Mouse: '+str(mouse.get())
    sliceNb='Slice: '+str(slice2.get())
    trialNb='Trial: '+str(exp.get())
    allmemo=mainStruct["allmemo"]
    initvNb='Initial stim intensity: '+ str(initv.get())+'V'
    if mainStruct["logSteps"]:
        stepvNb='Stim increment (log steps, x(1+increment)):'+ str(stepv.get())
    else:
        stepvNb='Stim increment:'+ str(stepv.get())+'V'
    nstimNb= 'Number of stim in the series: '+ str(nstim.get())
    nrepNb='Number of series repetitions: '+str(nrep.get())
    stimdurNb='Stim duration: ' + str (stimdur.get())+'ms'
    isiNb= 'Stim interval: '+str(isi.get())+'s'
    if Bipolar.get():
        bipolar=1
        bipolarNb='Bipolar stimulation'
    else:
        bipolar=0
        bipolarNb='Monopolar stimulation'  
    mainStruct["trial"]=exp.get()
    mainStruct["bipolar"]=bipolar
    mainStruct["memo"]=memo.get()
    mainStruct["slice"]=slice2.get()
    state='Full run completed'
    if not PreviewMode.get():
      # the numstim column records LogSteps as a negative number of stims
      trialStruct=dict(mainStruct)
      if mainStruct["logSteps"]:
          trialStruct["ns"]=-mainStruct["ns"]
      trialID=addTrialData(trialStruct)
    else:
      trialID=-1
      state='Interrupt after: '+mainStruct["curRun"]+' of '+ str(nrep.get()) + ' Runs and after '+ mainStruct["curStim"]+' of '+ str(nstim.get()) +' Stims of this Run'
    allnote='Date: '+d+', '+'Block: '+mainStruct["block"]+', '+memoNote+', '+mouseNb+', '+sliceNb+', '+trialNb+', TrialID: '+str(trialID)+', memo changes:'+allmemo 
    stimparam= initvNb+', '+stepvNb+', '+nstimNb+', '+nrepNb+', '+stimdurNb+', '+isiNb+ ', '+bipolarNb
    mouseInfo=mouseList.get()
    ttank.AppendNote(project)
    ttank.AppendNote(mouseInfo)
    aa=ttank.AppendNote(allnote)
    #print('allnote write result',aa)
    ttank.AppendNote(stimparam)
    ttank.AppendNote(state)
    stimbuffer.insert(INSERT,'\n'+mouseInfo)
    stimbuffer.insert(INSERT,'\n'+project)
    stimbuffer.insert(INSERT,'\n'+allnote)
    stimbuffer.insert(INSERT,'\n'+stimparam)
    exp.set(exp.get()+1)
    
    lblrunstatus.config(text='Idle')

def enableRecordButton():
    record['text']= "Start"
    record.state(['!disabled'])
          
# parameter files are read back as text, so "False" has to become False
def toBool(value):
    return str(value).strip().lower() in ('true','1','1.0','yes','on')

def updateMenu(mainStruct):
    numChans.set(mainStruct["nChan"])
    #print('updating menu')
    #print(mainStruct)
    initv.set(mainStruct["iniVal"])
    stepv.set(mainStruct["stepVal"])
    nstim.set(mainStruct["ns"])
    nrep.set(mainStruct["nr"]) 
    stimdur.set(mainStruct["stimDur"])
    Bipolar.set(mainStruct["bipolar"])
    isi.set(mainStruct["isiT"])
    # older parameter files may not have the train settings
    if "trainNP" in mainStruct:
        trainNP.set(mainStruct["trainNP"])
    if "trainFreq" in mainStruct:
        trainFreq.set(mainStruct["trainFreq"])
    # files saved before LogSteps existed mean linear steps
    LogSteps.set(toBool(mainStruct.get("logSteps",False)))
    #print('done updating menu')
    #print(mainStruct)

def fileOpen():
    
    thisFile=filedialog.askopenfilename(initialdir = paramsFolder,title="Select a Parameters File",filetypes = (("CSV files","*.csv"),))
    #print(thisFile)
    if thisFile and os.path.isfile(thisFile):
       # only the menu is updated; clickrecord copies the menu values into
       # mainStruct when a recording starts
       params=readDict2(thisFile)
       #print(params)
       updateMenu(params)

def fileSave():
    thisFileName=filedialog.asksaveasfilename(initialdir = paramsFolder,
       title="Select Parameters File Name to save",
       defaultextension = '.csv')
    #print(thisFileName)
    if (thisFileName):
        writeDict(thisFileName,mainStruct)
                       
       
# start main code:
fullParamsPath=paramsFolder+'recentv'+ParamsVersion+'.csv'
# a parameters file named on the command line (in paramsFolder, .csv optional)
# is loaded instead of the most recent one; exit still saves to fullParamsPath
loadParamsPath=fullParamsPath
if len(sys.argv)>1:
    loadParamsPath=os.path.join(paramsFolder,sys.argv[1])
    if not loadParamsPath.lower().endswith('.csv'):
        loadParamsPath+='.csv'
    if not os.path.isfile(loadParamsPath):
        sys.exit('parameters file not found: '+loadParamsPath)
    print('Loading parameters from '+loadParamsPath)

if os.path.isfile(loadParamsPath):
    mainStruct=readDict2(loadParamsPath)
mainStruct["plotStructLFP"]=[0,0,0,0,0,0]
mainStruct["plotStructCSD"]=[0,0,0,0,0,0]
mainStruct["recording"]=0
mainStruct["laststimtime"]=time.time()
mainStruct["tankfolder"]=0
mainStruct["allmemo"]=""
mainStruct.setdefault("nChan",16)
# older parameter files do not have logSteps
mainStruct["logSteps"]=toBool(mainStruct.get("logSteps",False))
try:
    import win32com.client
    import pywintypes
except:
    sys.exit('pywin32 package required')
os.chdir('C:/TDT/lib64')
try:
    # trying to load 64-bit version first
    tdt = win32com.client.Dispatch('TDevAcc.X')
    print('64 bit driver loaded!')
except:
    os.chdir('C:/TDT/lib')
    try:
        tdt = win32com.client.Dispatch('TDevAcc.X')
        print('Try 32 bit driver')
    except:
        # neither 32-bit nor 64-bit version could be loaded
        sys.exit('could not load TDevAcc.ocx')
ttank = win32com.client.Dispatch('TTank.X')
# connect to the tank server and the TDT; returns an error message, or '' once
# the TDT reports a device (ConnectServer can return 1 before it really is
# connected, so the device name is the real test)
def connectTDT():
    # rebind the module level objects so the rest of the script uses the
    # connections made here
    global tdt, ttank
    print('Attempting to connect to TDT ...')
    try:
        ttank = win32com.client.Dispatch('TTank.X')
        if ttank.ConnectServer('Local','Me') != 1:
            return 'could not connect to Tank'
        tdt = win32com.client.Dispatch('TDevAcc.X')
        if tdt.ConnectServer('Local') != 1:
            return 'could not connect to Workbench / Synapse'
        # give the hardware a moment to register before asking for the device
        time.sleep(1)
        if not tdt.GetDeviceName(0):
            return 'TDT lied.  We were not actually connected'
    except pywintypes.com_error as e:
        return 'COM error: '+str(e)
    print('Successfully connected to device: '+tdt.GetDeviceName(0))
    return ''

# keep trying until the TDT is up, e.g. while OpenEx is still starting;
# Ctrl+C in this console gives up
attempt=1
msg=connectTDT()
while msg:
    print('Attempt {:d}: {:s}, trying again in {:g}s'.format(attempt,msg,connectRetry))
    # shut down the partial connections before the next try, 6/25/20 jrh
    try:
        ttank.CloseTank()
        tdt.CloseConnection()
        ttank.ReleaseServer()
    except pywintypes.com_error:
        pass
    time.sleep(connectRetry)
    attempt+=1
    msg=connectTDT()
   
stimsize=tdt.GetTargetSize('RZ5.StimBuffIn')
deviceName=tdt.GetDeviceName(0)
print('Device name #0 =',tdt.GetDeviceName(0))
print('Device RCO file =',tdt.GetDeviceRCO(tdt.GetDeviceName(0)))
print('Device status=',tdt.GetDeviceStatus(tdt.GetDeviceName(0)))

root = Tk()
#TDT controller main window
window=Toplevel(root)
window.geometry('+900+1')
graphwindow=Toplevel(root)
graphwindow.withdraw()
mouseWindow=Toplevel(root)
mouseWindow.geometry('+400+100')
mouseWindow.attributes("-topmost", True)
fileWindow=Toplevel(root)
fileWindow.geometry('250x120+400+100')
fileWindow.attributes("-topmost", True)
fileWindow.withdraw()
#mouseWindow.withdraw()
root.iconify() 
d=time.strftime('%Y%m%d',time.localtime())
# Idle mode
tdt.SetSysMode(0)
run=1
stim=0
validMouse=0

############TDT controller window###########################################
buffer= []
r=0;
window.title("TDT Controller")

lblt = ttk.Label(window)
lblt.grid(column=0, row=r)
lbldt = ttk.Label(window, text=d)
lbldt.grid(column=1, row=r)
r+=1

numChans=IntVar()
numChans.set(mainStruct["nChan"])
lblnc = ttk.Label(window, text="Number of Channels")
lblnc.grid(column=0, row=r)
txt = ttk.Entry(window,width=5,textvariable=numChans)
txt.grid(column=1, row=r)
r+=1

initv=DoubleVar()
initv.set(mainStruct["iniVal"])
lbl = ttk.Label(window, text="Initial Stim Intensity (V)")
lbl.grid(column=0, row=r)
txt = ttk.Entry(window,width=5,textvariable=initv)
txt.grid(column=1, row=r)

r+=1
stepv=DoubleVar()
stepv.set(mainStruct["stepVal"])
lbl2 = ttk.Label(window, text="Stimulus Increment (V)")
lbl2.grid(column=0, row=r)
txt2 = ttk.Entry(window,width=5,textvariable=stepv)
txt2.grid(column=1, row=r)

r+=1
nstim=IntVar()
nstim.set(mainStruct["ns"])
lbl3 = ttk.Label(window, text="Number of Stim. in series")
lbl3.grid(column=0, row=r)
numstim = ttk.Spinbox(window, from_=0, to=100, width=5,textvariable=nstim)
numstim.grid(column=1, row=r)

r+=1
nrep =IntVar() 
nrep.set(mainStruct["nr"]) 
lbl4 = ttk.Label(window, text="Number series repeats")
lbl4.grid(column=0, row=r)
numreps = ttk.Spinbox(window, from_=0, to=100, width=5,textvariable=nrep)
numreps.grid(column=1, row=r)

r+=1
stimdur=DoubleVar()
stimdur.set(mainStruct["stimDur"])
lblsd = ttk.Label(window, text="Stimulus Duration (ms)")
lblsd.grid(column=0, row=r)
txtsd = ttk.Entry(window,width=5,textvariable=stimdur)
txtsd.grid(column=1, row=r)

r+=1
isi=DoubleVar()
isi.set(mainStruct["isiT"])
lbl = ttk.Label(window, text="InterStimulus Interval (s)")
lbl.grid(column=0, row=r)
txtisi = ttk.Entry(window,width=5,textvariable=isi)
txtisi.grid(column=1, row=r)

r+=1
trainNP=IntVar()
trainNP.set(mainStruct["trainNP"])
lblnp = ttk.Label(window, text="Train n pulses")
lblnp.grid(column=0, row=r)
txtnp = ttk.Entry(window,width=5,textvariable=trainNP)
txtnp.grid(column=1, row=r)

r+=1
trainFreq=DoubleVar()
trainFreq.set(mainStruct["trainFreq"])
lbtf = ttk.Label(window, text="Train Freq.(Hz)")
lbtf.grid(column=0, row=r)
txttf = ttk.Entry(window,width=5,textvariable=trainFreq)
txttf.grid(column=1, row=r)

r+=1
prjt=StringVar()
lblproj = ttk.Label(window, text="Project Title")
lblproj.grid(column=0, row=r)
txtproj = ttk.Entry(window,width=10,textvariable=prjt)
txtproj.grid(column=1, row=r)

r+=1
memo=StringVar()
lblmemo = ttk.Label(window, text="Memo")
lblmemo.grid(column=0, row=r)
txtmemo = ttk.Entry(window,width=10,textvariable=memo)
txtmemo.grid(column=1, row=r)

r+=1
mouse=IntVar()
mouse.set(1)
lblm = ttk.Label(window, text="Mouse #")
lblm.grid(column=0, row=r)
mice = ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=mouse)
mice.grid(column=1,row=r)

r+=1
slice2=IntVar()
slice2.set(1)
lbls = ttk.Label(window, text="Slice #")
lbls.grid(column=0, row=r)
slices = ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=slice2)
slices.grid(column=1,row=r)

r+=1
exp=IntVar()
exp.set(1)
lble = ttk.Label(window, text="Trial #")
lble.grid(column=0, row=r)
exps = ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=exp)
exps.grid(column=1,row=r)

r+=1
PreviewMode= IntVar()
PreviewMode.set(1)
previewBtn = ttk.Checkbutton(window, text="Preview Mode",variable=PreviewMode)
previewBtn.grid(column=0, row=r)
Bipolar= BooleanVar()
Bipolar.set(True)
ckbtn = ttk.Checkbutton(window,text="Bipolar",variable=Bipolar)
ckbtn.grid(column=1,row=r)
ckbtn.state(["selected"])

r+=1
LogSteps= BooleanVar()
LogSteps.set(mainStruct["logSteps"])
logBtn = ttk.Checkbutton(window,text="LogSteps",variable=LogSteps)
logBtn.grid(column=0,row=r)

r+=1
closeFig= IntVar()
closeFig=ttk.Button (window, text='CloseFig', command=closeallFig)
closeFig.grid(column=0,row=r)
fileMode = ttk.Button(window,text="Files",command=lambda:onClick(fileWindow))
fileMode.grid(column=1,row=r)

MUAMode= 1
#IntVar()
#MUAMode.set(mainStruct["doMUA"])
#MUABtn = ttk.Checkbutton(window, text="MUA",variable=MUAMode)
#MUABtn.grid(column=1, row=r)

r+=1
plotBtn = ttk.Button(window, text="Plot Menu",command=lambda:onClick(graphwindow))
plotBtn.grid(column=0, row=r)
mouseMode = ttk.Button(window,text="Mouse Menu",command=lambda:onClick(mouseWindow))
mouseMode.grid(column=1,row=r)

r+=2
record = ttk.Button(window, text="START", command=clickrecord)
record.grid(columnspan=2,row=r,padx=1)
lblrunstatus = ttk.Label(window, text='idle', font='Arial 8 bold')
lblrunstatus.grid(column=1, row=r)

r+=1
stimbuffer = scrolledtext.ScrolledText(window,width=30,height=2)
r+=10
stimbuffer.grid(columnspan=2,row=r,padx=15)
clock()

r+=1
Exit= IntVar()
Exit = ttk.Button(window, text="EXIT", command=exitTDT)
Exit.grid(columnspan=2,row=r,padx=1)


#################File window#########################################

r=0  # reset row number to zero because we are starting over in a new # tkinter window
fileWindow.title("Parameter File")
r+=1
fileRead = ttk.Button(fileWindow, text="Open File", command=fileOpen)# need to define the command here 
fileRead.grid(row=r,pady=5,padx=5)
r+=1
fileWrite = ttk.Button(fileWindow, text="Save File", command=fileSave)# need to define the command here 
fileWrite.grid(row=r,pady=5,padx=5)
r+=1
okFile = ttk.Button(fileWindow, text="OK", command=lambda:withdrawWindow(fileWindow))# need to define the command here 
okFile.grid(row=r,pady=5,padx=5)



#################Mouse window#########################################

r=0  # reset row number to zero because we are starting over in a new # tkinter window
mouseWindow.title("Mouse choice")
labelTop = tk.Label(mouseWindow, text = "Which Mouse will you use today?",font='Arial 11 bold')
labelTop.grid(row=r,pady=5,padx=2)
r+=1
# select the first item in list
mouseListing=gettodaysmice()
#print(mouseListing)
r+=1
projects=getprojects()
numberOfElements=len(mouseListing)
numberOfProjectElements=len(projects)
mouseListingForCombo=[]
projectListingForCombo=[]
mouseList = ttk.Combobox(mouseWindow, values=[],width=50)
#print(numberOfElements)   
if mouseListing:
   validMouse=1
   for i in range ( 0 , numberOfElements):
       curMouse=mouseListing[i]
#       print(i)
       
       if len(curMouse[2])<1:
           strain="empty"
       else:
           strain=list(curMouse[2])[0]
       #if len:
           
       #print(curMouse)
       #if len(mouseListing[i][2])<1: # need to put in a strain so that tdt code doesn't choke
       #    strain="empty"
       thisMouseDesc='None'
       if type(curMouse) is tuple:
           diff=curMouse[6]-date.today()
           mouseAge='p'+str(abs(diff.days))
           
           thisMouseDesc='Strain:{:s} ID/eartag:{:d}/{:d} {:s}{:s} {:s}'.format(strain,curMouse[0],curMouse[3], mouseAge,curMouse[4],curMouse[8])
       mouseListingForCombo.append(thisMouseDesc)
   mouseList.config(values=mouseListingForCombo)
   mouseList.current(numberOfElements-1) # set default to first mouse
   mouseList.grid(row=r,pady=5)
   r+=1
   numberOfProjectElements=len(projects)
   projectListingForCombo=[]
if projects:
    labelTop2 = tk.Label(mouseWindow, text = "Which Project will you use today?",font='Arial 11 bold')
    labelTop2.grid(row=r,pady=5,padx=2)
    r+=1
    projectList = ttk.Combobox(mouseWindow, values=[],width=30)
    projectList.grid(row=r,pady=5,padx=2)
    for i in range ( 0 , numberOfProjectElements):
        curProject=projects[i][0]
        projectListingForCombo.append(curProject)
    projectList.config(values=projectListingForCombo)
    projectList.current(numberOfProjectElements-1) # set default to first mouse
    r+=1
    projectList.grid(row=r,pady=5)

r+=1

okMouse = ttk.Button(mouseWindow, text="OK", command=lambda:withdrawWindow(mouseWindow))# need to define the command here 
okMouse.grid(row=r,pady=5)

##################Plot Window######
r=0  # reset row number to zero because we are starting over in a new # tkinter window
graphwindow.title("Plot Parameters")

r+=1
baselineOffset= BooleanVar()
baselineOffset.set(mainStruct["baselineOffset"])
offsetBtn = ttk.Checkbutton(graphwindow, text="Baseline Offset",variable=baselineOffset)
offsetBtn.grid(column=0, row=r,columnspan=4)

r+=1
plotModeLFP= BooleanVar()
plotModeLFP.set(mainStruct["doLFP"])
plotBtn = ttk.Checkbutton(graphwindow, text="Plot LFP",variable=plotModeLFP)
plotBtn.grid(column = 1, row=r)

gainLFP=DoubleVar()
gainLFP.set(mainStruct["gainLFP"])
lblgainLFP = ttk.Label(graphwindow, text="Gain LFP" )
lblgainLFP.grid(column=2, row=r)
txtgainLFP = ttk.Entry(graphwindow,width=5,textvariable=gainLFP)
txtgainLFP.grid(column=3, row=r)

r+=1
plotModeCSD= BooleanVar()
plotModeCSD.set(mainStruct["doCSD"])
plotCSDBtn = ttk.Checkbutton(graphwindow, text="Plot CSD", variable=plotModeCSD)
plotCSDBtn.grid(column=1, row=r)
gainCSD=DoubleVar()
gainCSD.set(mainStruct["gainCSD"])
lblgainCSD = ttk.Label(graphwindow, text="Gain CSD")
lblgainCSD.grid(column=2, row=r)
txtgainCSD = ttk.Entry(graphwindow,width=5,textvariable=gainCSD)
txtgainCSD.grid(column=3, row=r)

r+=1
# so this is the table title row.
tablelabel1 = ttk.Label(graphwindow, text="")
tablelabel1.grid(column=0, row=r)
tablelabel1 = ttk.Label(graphwindow, text="Channel")
tablelabel1.grid(column=1, row=r)
tablelabel1 = ttk.Label(graphwindow, text="Begin (ms)")
tablelabel1.grid(column=2, row=r)
tablelabel1 = ttk.Label(graphwindow, text="End (ms)")
tablelabel1.grid(column=3, row=r)

r+=1
# now we make the content rows
preStimDisplay=DoubleVar()
preStimDisplay.set(mainStruct["preStimTime"])
lblpreStimDisplay = ttk.Label(graphwindow, text="Display")
lblpreStimDisplay.grid(column=0, row=r)
txtpreStimDisplay = ttk.Entry(graphwindow,width=5,textvariable=preStimDisplay)
txtpreStimDisplay.grid(column=2, row=r)

postStimDisplay=DoubleVar()
postStimDisplay.set(mainStruct["postStimTime"])
txtpostStimDisplay = ttk.Entry(graphwindow,width=5,textvariable=postStimDisplay)
txtpostStimDisplay.grid(column=3, row=r)

# this row is the first channel to measure
r+=1
ch1=IntVar()
ch1.set(mainStruct["plotChannelA"])
lblch1 = ttk.Label(graphwindow, text="Meas. A")
lblch1.grid(column=0, row=r)
txtch1 = ttk.Entry(graphwindow,width=5,textvariable=ch1)
txtch1.grid(column=1,row=r)

start1=DoubleVar()
start1.set(mainStruct["1stMeasureBegin"])
txtstart1 = ttk.Entry(graphwindow,width=5,textvariable=start1)
txtstart1.grid(column=2, row=r)

end1=DoubleVar()
end1.set(mainStruct["1stMeasureEnd"])
txtend1 = ttk.Entry(graphwindow,width=5,textvariable=end1)
txtend1.grid(column=3, row=r)

# this row is the second channel to measure
r+=1
ch2=IntVar()
ch2.set(mainStruct["plotChannelB"])
lblch2 = ttk.Label(graphwindow, text="Meas. B")
lblch2.grid(column=0, row=r)
txtch2 = ttk.Entry(graphwindow,width=5,textvariable=ch2)
txtch2.grid(column=1,row=r)

start2=DoubleVar()
start2.set(mainStruct["2ndMeasureBegin"])
txtstart2 = ttk.Entry(graphwindow,width=5,textvariable=start2)
txtstart2.grid(column=2, row=r)

end2=DoubleVar()
end2.set(mainStruct["2ndMeasureEnd"])
txtend2 = ttk.Entry(graphwindow,width=5,textvariable=end2)
txtend2.grid(column=3, row=r)

r+=1
okPlot= IntVar()
btn_text = StringVar()
okPlot = ttk.Button(graphwindow, text="OK", command=lambda:withdrawWindow(graphwindow))# need to define the command here 
okPlot.grid(columnspan=4,row=r,padx=1)
#########

window.mainloop()

