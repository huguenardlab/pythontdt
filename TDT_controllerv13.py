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
# version 13: consistent camelCase names (Tk variables end in Var, widgets in
# Label/Entry/Spin/Check/Btn), clearer parameter keys (see renamedKeys; older
# parameter files are translated on load), uses micedbv6 and plotLFP_CSDv5
# which take the new keys, and fixes the episodeTag reset
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import Text
from tkinter import *
from micedbv6 import *
from tkinter import ttk
from offset_baseline import *
from plotLFP_CSDv5 import *
from dict2file import *
import tkinter as tk
import re
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
# version 10 files use the renamed keys; a version 9 file is translated
paramsVersion='10'
oldParamsVersion='9'
tdtTimeout=10 # seconds to wait for the sweeps of one stim before giving up
acquisitionJob=None # id of the pending window.after call for acquisitionLoop
connectRetry=10 # seconds between attempts to connect to the TDT at startup
# circuit tag of the episode counter shown in OpenEx, set to 0 on each Start;
# leave empty to rely on the Idle->Preview/Record mode change to reset it
episodeTag=''
registeredTank=None # tank folder already registered with AddTank/SetTankName
mainStruct= { 
  "baselineOffset": False,  
  "stimDur":0.1,
  "preStimTime": 1,
  "postStimTime": 5,
  "plotChannelA": 13,
  "plotChannelB": 0,
  "measure1Begin": 3,
  "measure1End": 3.5,
  "measure2Begin": 2,
  "measure2End": 3,
  "gainLFP":-0.0005,
  "gainCSD":-0.025,
  "doLFP": True,
  "doCSD": True,
  "doMUA": False,
  "stimDelay": 0,
  "plotStructLFP":[0,0,0,0,0,0],
  "plotStructCSD":[0,0,0,0,0,0],
  "restart":0,
    "run":0,
    "recording":0,
    "stim":0,
    "isi":15,
    "initialStim":1,
    "stimStep":1,
    "nRepeats":8,
    "nStims":1,
    "lastStimTime":0,
    "project":0,
    "slice":0,
    "block":0,
    "curRun":0,
    "curStim":0,
    "thisSweep":0,
    "mouseID":0,
    "tankFolder":0,
    "nChan":16,
    "waitingForTrigger":0,
    "waitingForTDT":0,
    "oldMemo":'',
    "allMemo":'',
    "trainPulses":1,
    "trainFreq":100,
    "logSteps":False,
    "sweepCount":0,
    "tdtWaitStart":0
}
# keys renamed in version 13, old name: new name
renamedKeys={
    "thissweep":"thisSweep",
    "laststimtime":"lastStimTime",
    "tankfolder":"tankFolder",
    "oldmemo":"oldMemo",
    "allmemo":"allMemo",
    "nr":"nRepeats",
    "ns":"nStims",
    "isiT":"isi",
    "iniVal":"initialStim",
    "stepVal":"stimStep",
    "trainNP":"trainPulses",
    "1stMeasureBegin":"measure1Begin",
    "1stMeasureEnd":"measure1End",
    "2ndMeasureBegin":"measure2Begin",
    "2ndMeasureEnd":"measure2End",
}
# read a parameters file, translating the keys of files saved before v13
def readParams(fileName):
    params=readDict2(fileName)
    for oldKey,newKey in renamedKeys.items():
        if oldKey in params:
            params[newKey]=params.pop(oldKey)
    return params

# here is where you go when you click start
def onRecordClick():
    print("click record")
#    if mainStruct["doMUA"]:
#        mainStruct["nChan"]=1
    if mainStruct["recording"] :
     mainStruct["recording"]=0
     # deliverStim() shows "Stopping..." and sets the button back to Start
     # once the run is finalized
     mainStruct["run"]=1000
     mainStruct["stim"]=1000
     mainStruct["restart"]=1
     # clear the wait flags so acquisitionLoop cannot trigger deliverStim again
     # (which would finalize the run a second time) or keep polling the tank
     mainStruct["waitingForTrigger"]=0
     mainStruct["waitingForTDT"]=0
     if mainStruct["nChan"]<3:
       mainStruct["doCSD"]=0
       # cannot do CSD if there are less than 3 channels
     deliverStim()
    else:
        recordBtn['text']= "Stop"
        mainStruct["lastStimTime"]=time.time()-10000
        mainStruct["waitingForTrigger"]=1
        registerTank()
        tdt.SetTargetVal('RZ5.BipolarStim',bipolarVar.get())
        tdt.SetTargetVal('RZ5.StimDuration',stimDurVar.get())
        mainStruct["recording"]=1
        if previewModeVar.get():
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
    projectName=projectVar.get()
    # if user fails to specify project it will use the TEST project
    if projectName=='':
      projectName='TEST'
      projectVar.set(projectName)
    projectFolder='D:/TDTdata/'+projectName
    tankFolder=projectFolder.replace('/','\\')+'\\'+today
    mainStruct["tankFolder"]=tankFolder
    if tankFolder==registeredTank:
        return
    tankAdded=ttank.AddTank(today,'REGISTER@'+projectFolder)
    if tankAdded:
       print('New Tank Added: '+projectFolder)
    else:
        print('ERROR! New Tank '+projectFolder+' was not added.')
        window.destroy()
        sys.exit()
    tankNamed=tdt.SetTankName(tankFolder)
    if tankNamed:
        print('New Tank Name: '+tankFolder)
    else:
        print('ERROR! Could not name new tank '+tankFolder)
        window.destroy()
        sys.exit()
    registeredTank=tankFolder
    logText.insert(INSERT,'\nTank: '+tankFolder)

def startRun():
        if not mainStruct["recording"]:
            return # Stop was pressed during the one second wait
        if episodeTag:
            # start the episode count displayed in OpenEx from 0 for this run
            tdt.SetTargetVal(episodeTag,0)
#        mainStruct["doMUA"]=MUAMode.get()
        mainStruct["nRepeats"]=nRepeatsVar.get()
        mainStruct["nStims"]=nStimsVar.get()
        mainStruct["stimDur"]=stimDurVar.get()
        mainStruct["initialStim"]=initialStimVar.get()
        mainStruct["stimStep"]=stimStepVar.get()
        mainStruct["logSteps"]=logStepsVar.get()
        mainStruct["isi"]=isiVar.get()
        mainStruct["bipolar"]=bipolarVar.get()
        mainStruct["trainPulses"]=trainPulsesVar.get()
        mainStruct["trainFreq"]=trainFreqVar.get()
        mainStruct["nChan"]=nChanVar.get()        
        mainStruct["run"]=1
        mainStruct["stim"]=0
        ttank.OpenTank(today,'R')
        mainStruct["oldMemo"]=memoVar.get()
        mainStruct["block"]=ttank.GetHotBlock()
        mainStruct["sweepCount"]=0 # new block, no sweeps read yet
        mainStruct["waitingForTDT"]=0
        startAcquisitionLoop()

# schedule acquisitionLoop, cancelling any pending call first so that only one
# loop is ever running
def startAcquisitionLoop():
    global acquisitionJob
    if acquisitionJob is not None:
        window.after_cancel(acquisitionJob)
    acquisitionJob=window.after(100,acquisitionLoop)

def clock():
    # acquisitionLoop updates the label while recording
    if mainStruct["recording"]<1:
        t=time.strftime('%I:%M:%S %p',time.localtime())+'{: 4.0f}'.format(time.time()-mainStruct["lastStimTime"])
        clockLabel.config(text=t)
    window.after(1000,clock)

def showWindow(win):
    win.deiconify()

def hideWindow(win):
    win.withdraw()

# OK in the mouse window: keep the chosen mouse and project, then hide it
def acceptMouseChoice():
    mouseInfo=mouseCombo.get()
    if projects:
        projectName=projectCombo.get()
        projectVar.set(projectName) # show it in the main window
        mainStruct["project"]=projectName
    # the text after "ID/eartag:" up to the age, e.g. 1234/56
    idMatch=re.findall('eartag:(.*) p',mouseInfo)
    if idMatch:
        mainStruct["mouseID"]=idMatch[0]
    else:
        mainStruct["mouseID"]=0
    hideWindow(mouseWindow)

#Close all figure
def closeAllFigures():
    plt.close('all')
    
#Exit TDT properly
def exitController():
    print ('Exit has been pressed')
    ttank.CheckTank(today)
    ttank.CloseTank()
    tdt.CloseConnection()
    ttank.ReleaseServer()
    window.destroy()
    mouseWindow.destroy()
    plotWindow.destroy()
    fileWindow.destroy()
    root.destroy()
    writeDict(recentParamsPath,mainStruct)
    closeAllFigures()
    sys.exit()
    

#trigger the stim, create and store Notes
def acquisitionLoop():
    global acquisitionJob
    acquisitionJob=None
    try:
        acquisitionStep()
    except Exception:
        # print the error but keep the loop alive
        traceback.print_exc()
    finally:
        # only one loop: it stops when recording stops and onRecordClick
        # starts it again through startAcquisitionLoop
        if mainStruct["recording"] and acquisitionJob is None:
            acquisitionJob=window.after(100,acquisitionLoop)

def acquisitionStep():
    timeLeft=mainStruct["lastStimTime"]+mainStruct["isi"]-time.time()
    #print(timeLeft)
    t=time.strftime('%I:%M:%S %p',time.localtime())
    if mainStruct["recording"]:
        t=t+': Next Stim in '+'{:4.1f}s'.format(timeLeft)
        if t!='':
          clockLabel.config(text=t)                        
    if mainStruct["waitingForTrigger"]:
        now=time.time()
        if now-mainStruct["lastStimTime"]>mainStruct["isi"]:
            mainStruct["waitingForTrigger"]=0
            deliverStim()
    if mainStruct["waitingForTDT"]:
        nChan=int(mainStruct["nChan"])
        # check the timeout first so it still fires if the tank reads fail
        timedOut=time.time()-mainStruct["tdtWaitStart"]>tdtTimeout
        ttank.OpenTank(today,'R')
        mainStruct["block"]=ttank.GetHotBlock()
        ttank.SelectBlock(mainStruct["block"])
        # sweepCount is the number of sweeps already read in this block, so
        # the stim is done when nChan more have arrived
        expectedSweeps=mainStruct["sweepCount"]+nChan
        nSweeps = ttank.ReadEventsSimple('SSwp')
        if nSweeps<expectedSweeps:
            if timedOut:
                msg='No data from TDT after {:d}s ({:d} of {:d} sweeps), skipping Run {:s} Stim {:s}'.format(tdtTimeout,nSweeps-mainStruct["sweepCount"],nChan,mainStruct["curRun"],mainStruct["curStim"])
                print(msg)
                logText.insert(INSERT,'\n'+msg)
                # resynchronize on what is in the tank and go on to the next stim
                mainStruct["sweepCount"]=nSweeps
                mainStruct["waitingForTDT"]=0
                mainStruct["waitingForTrigger"]=1
            return
        if nSweeps>expectedSweeps:
            print('Warning: expected {:d} sweeps, tank has {:d}, using the last {:d}'.format(expectedSweeps,nSweeps,nChan))
        # read only the sweeps of this stim instead of the whole block
        data = ttank.ParseEvV(nSweeps-nChan, nChan)
        sweepData = np.array(data)
        if np.ndim(sweepData)==1:
            sweepData=sweepData.reshape(-1,1)
        # stimDelay uses the first sweep and first stim of the block
        timeStamps=ttank.ParseEvInfoV(0,1,6)
        #print(timeStamps)
        # reading the EpcV events makes ParseEvInfoV return the stim times
        ttank.ReadEventsSimple('EpcV')
        stimStamps=ttank.ParseEvInfoV(0,1,6)
        if stimStamps is None:
            # for some reason TDT is not reading out stimStamps reliably
            # with this new controller #11, so setting the delay to
            # what is should be for the block_store_1_4Ch, which is 400 ms
            stimStamps=(timeStamps[0]+.4,)
        #print(stimStamps)
        if nChan==16:
            # 16 channel probe mapping: keep channel 0, reverse 1..15
            channelOrder=range(15,0,-1)
            channelOrder=np.insert(channelOrder,0,0)
            mainStruct["thisSweep"]=sweepData[:,channelOrder]
        else:
            mainStruct["thisSweep"]=sweepData
        mainStruct["sweepCount"]=nSweeps
        mainStruct["waitingForTDT"]=0
        mainStruct["waitingForTrigger"]=1
        #Calculus of the Stimdelay here because it needs to wait to have data in the time/ stim Stamps 
        mainStruct["stimDelay"]=stimStamps[0]-timeStamps[0]
        if baselineOffsetVar.get():
            mainStruct["thisSweep"]=offsetTDT(mainStruct["thisSweep"])
        if plotLFPVar.get() or plotCSDVar.get():
            mainStruct["plotChannelA"]=channelAVar.get()
            mainStruct["plotChannelB"]=channelBVar.get()
            mainStruct["measure1Begin"]=measure1BeginVar.get()
            mainStruct["measure1End"]=measure1EndVar.get()
            mainStruct["measure2Begin"]=measure2BeginVar.get()
            mainStruct["measure2End"]=measure2EndVar.get() 
            mainStruct["gainLFP"]=gainLFPVar.get()
            mainStruct["gainCSD"]=gainCSDVar.get()
            mainStruct["doLFP"]=plotLFPVar.get()
            mainStruct["doCSD"]=plotCSDVar.get()
            mainStruct["preStimTime"]=preStimTimeVar.get()
            mainStruct["postStimTime"]=postStimTimeVar.get()
            plotTDTdata(mainStruct)

def deliverStim() :
    if mainStruct["run"]<=mainStruct["nRepeats"] :
      if mainStruct["stim"]<mainStruct["nStims"] :
        mainStruct["stim"]+=1
        if mainStruct["logSteps"]:
            # log steps: each stim is (1+increment) times the one before
            mainStruct["thisStim"]=mainStruct["initialStim"]*(1+mainStruct["stimStep"])**(mainStruct["stim"]-1)
        else:
            mainStruct["thisStim"]=mainStruct["initialStim"]+ (mainStruct["stim"]-1)*mainStruct["stimStep"]
        runStatusLabel.config(text='Run '+str(mainStruct["run"])+' Stim '+str(mainStruct["stim"])+'{: .1f}'.format(mainStruct["thisStim"])+'V')
        mainStruct["curRun"]=str(mainStruct["run"])
        mainStruct["curStim"]=str(mainStruct["stim"])
        #print("oneStim")
        # send out current stimulus va
        tdt.SetTargetVal('RZ5.SingleStimValue',mainStruct["thisStim"])
        tdt.SetTargetVal('RZ5.StimEnable',1)
        
        tdt.SetTargetVal('RZ5.StimIndex',mainStruct["stim"])
        tdt.SetTargetVal('RZ5.StimDuration',stimDurVar.get())
        tdt.SetTargetVal('RZ5.BipolarStim',bipolarVar.get())
        tdt.SetTargetVal('RZ5.trainNP',trainPulsesVar.get())
        tdt.SetTargetVal('RZ5.trainInterval',(1000/trainFreqVar.get())-.1)
        # trigger a sweep with a rising edge signal
        tdt.SetTargetVal('RZ5.SingleStimTrigger',1)
        # reset SingleStimTrigger value to 0, so that it can be triggered next time
        # the assumption is that the trigger has actually already been detected.
        tdt.SetTargetVal('RZ5.SingleStimTrigger',0)
        mainStruct["lastStimTime"]=time.time()
        mainStruct["waitingForTDT"]=1;
        mainStruct["tdtWaitStart"]=time.time()
        newMemo=memoVar.get()
        if newMemo!=mainStruct["oldMemo"]:
            mainStruct["oldMemo"]=newMemo
            mainStruct["allMemo"]=mainStruct["allMemo"]+" [Run #" + str(mainStruct["run"])+ ", Changed Condition:" +newMemo + " at " +time.strftime('%I:%M:%S %p',time.localtime())+"]"
      else :
        mainStruct["run"]+=1
        mainStruct["stim"]=0
        deliverStim()
    else :
        # DONE WITH STIMS AND RUNS
        # show the stop and disable the button before the slow end-of-run
        # work, so clicks made during it are ignored instead of being queued
        # and starting a new recording
        recordBtn['text']= "Stopping..."
        recordBtn.state(['disabled'])
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
    ttank.OpenTank(mainStruct['tankFolder'],'R')
    ttank.OpenTank(today,'R')
    ttank.SelectBlock(mainStruct["block"])
    projectNote='Project: '+projectVar.get()
    memoNote='Memo: '+ memoVar.get()
    mouseNote='Mouse: '+str(mouseVar.get())
    sliceNote='Slice: '+str(sliceVar.get())
    trialNote='Trial: '+str(trialVar.get())
    allMemo=mainStruct["allMemo"]
    initialStimNote='Initial stim intensity: '+ str(initialStimVar.get())+'V'
    if mainStruct["logSteps"]:
        stimStepNote='Stim increment (log steps, x(1+increment)):'+ str(stimStepVar.get())
    else:
        stimStepNote='Stim increment:'+ str(stimStepVar.get())+'V'
    nStimsNote= 'Number of stim in the series: '+ str(nStimsVar.get())
    nRepeatsNote='Number of series repetitions: '+str(nRepeatsVar.get())
    stimDurNote='Stim duration: ' + str (stimDurVar.get())+'ms'
    isiNote= 'Stim interval: '+str(isiVar.get())+'s'
    if bipolarVar.get():
        bipolar=1
        bipolarNote='Bipolar stimulation'
    else:
        bipolar=0
        bipolarNote='Monopolar stimulation'  
    mainStruct["trial"]=trialVar.get()
    mainStruct["bipolar"]=bipolar
    mainStruct["memo"]=memoVar.get()
    mainStruct["slice"]=sliceVar.get()
    state='Full run completed'
    if not previewModeVar.get():
      # the numstim column records LogSteps as a negative number of stims
      trialStruct=dict(mainStruct)
      if mainStruct["logSteps"]:
          trialStruct["nStims"]=-mainStruct["nStims"]
      trialID=addTrialData(trialStruct)
    else:
      trialID=-1
      state='Interrupt after: '+mainStruct["curRun"]+' of '+ str(nRepeatsVar.get()) + ' Runs and after '+ mainStruct["curStim"]+' of '+ str(nStimsVar.get()) +' Stims of this Run'
    allNote='Date: '+today+', '+'Block: '+mainStruct["block"]+', '+memoNote+', '+mouseNote+', '+sliceNote+', '+trialNote+', TrialID: '+str(trialID)+', memo changes:'+allMemo 
    stimParams= initialStimNote+', '+stimStepNote+', '+nStimsNote+', '+nRepeatsNote+', '+stimDurNote+', '+isiNote+ ', '+bipolarNote
    mouseInfo=mouseCombo.get()
    ttank.AppendNote(projectNote)
    ttank.AppendNote(mouseInfo)
    ttank.AppendNote(allNote)
    ttank.AppendNote(stimParams)
    ttank.AppendNote(state)
    logText.insert(INSERT,'\n'+mouseInfo)
    logText.insert(INSERT,'\n'+projectNote)
    logText.insert(INSERT,'\n'+allNote)
    logText.insert(INSERT,'\n'+stimParams)
    trialVar.set(trialVar.get()+1)
    
    runStatusLabel.config(text='Idle')

def enableRecordButton():
    recordBtn['text']= "Start"
    recordBtn.state(['!disabled'])
          
# parameter files are read back as text, so "False" has to become False
def toBool(value):
    return str(value).strip().lower() in ('true','1','1.0','yes','on')

def applyParamsToGui(params):
    nChanVar.set(params["nChan"])
    initialStimVar.set(params["initialStim"])
    stimStepVar.set(params["stimStep"])
    nStimsVar.set(params["nStims"])
    nRepeatsVar.set(params["nRepeats"])
    stimDurVar.set(params["stimDur"])
    bipolarVar.set(params["bipolar"])
    isiVar.set(params["isi"])
    # older parameter files may not have the train settings
    if "trainPulses" in params:
        trainPulsesVar.set(params["trainPulses"])
    if "trainFreq" in params:
        trainFreqVar.set(params["trainFreq"])
    # files saved before LogSteps existed mean linear steps
    logStepsVar.set(toBool(params.get("logSteps",False)))

def openParamsFile():
    fileName=filedialog.askopenfilename(initialdir = paramsFolder,title="Select a Parameters File",filetypes = (("CSV files","*.csv"),))
    if fileName and os.path.isfile(fileName):
       # only the GUI is updated; startRun copies the GUI values into
       # mainStruct when a recording starts
       applyParamsToGui(readParams(fileName))

def saveParamsFile():
    fileName=filedialog.asksaveasfilename(initialdir = paramsFolder,
       title="Select Parameters File Name to save",
       defaultextension = '.csv')
    if (fileName):
        writeDict(fileName,mainStruct)
                       
       
# start main code:
recentParamsPath=paramsFolder+'recentv'+paramsVersion+'.csv'
# a parameters file named on the command line (in paramsFolder, .csv optional)
# is loaded instead of the most recent one; exit still saves to recentParamsPath
loadParamsPath=recentParamsPath
if not os.path.isfile(loadParamsPath):
    # first run of v13: start from the settings v12 saved last
    loadParamsPath=paramsFolder+'recentv'+oldParamsVersion+'.csv'
if len(sys.argv)>1:
    loadParamsPath=os.path.join(paramsFolder,sys.argv[1])
    if not loadParamsPath.lower().endswith('.csv'):
        loadParamsPath+='.csv'
    if not os.path.isfile(loadParamsPath):
        sys.exit('parameters file not found: '+loadParamsPath)
    print('Loading parameters from '+loadParamsPath)

if os.path.isfile(loadParamsPath):
    # update keeps the defaults for keys an older file does not have
    mainStruct.update(readParams(loadParamsPath))
mainStruct["plotStructLFP"]=[0,0,0,0,0,0]
mainStruct["plotStructCSD"]=[0,0,0,0,0,0]
mainStruct["recording"]=0
mainStruct["lastStimTime"]=time.time()
mainStruct["tankFolder"]=0
mainStruct["allMemo"]=""
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
   
print('Device name #0 =',tdt.GetDeviceName(0))
print('Device RCO file =',tdt.GetDeviceRCO(tdt.GetDeviceName(0)))
print('Device status=',tdt.GetDeviceStatus(tdt.GetDeviceName(0)))

root = Tk()
#TDT controller main window
window=Toplevel(root)
window.geometry('+900+1')
plotWindow=Toplevel(root)
plotWindow.withdraw()
mouseWindow=Toplevel(root)
mouseWindow.geometry('+400+100')
mouseWindow.attributes("-topmost", True)
fileWindow=Toplevel(root)
fileWindow.geometry('250x120+400+100')
fileWindow.attributes("-topmost", True)
fileWindow.withdraw()
#mouseWindow.withdraw()
root.iconify() 
today=time.strftime('%Y%m%d',time.localtime())
# Idle mode
tdt.SetSysMode(0)

############TDT controller window###########################################
# widgets that are never referenced again are created and placed in one line
row=0
window.title("TDT Controller")

clockLabel = ttk.Label(window)
clockLabel.grid(column=0, row=row)
ttk.Label(window, text=today).grid(column=1, row=row)

row+=1
nChanVar=IntVar()
nChanVar.set(mainStruct["nChan"])
ttk.Label(window, text="Number of Channels").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=nChanVar).grid(column=1, row=row)

row+=1
initialStimVar=DoubleVar()
initialStimVar.set(mainStruct["initialStim"])
ttk.Label(window, text="Initial Stim Intensity (V)").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=initialStimVar).grid(column=1, row=row)

row+=1
stimStepVar=DoubleVar()
stimStepVar.set(mainStruct["stimStep"])
ttk.Label(window, text="Stimulus Increment (V)").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=stimStepVar).grid(column=1, row=row)

row+=1
nStimsVar=IntVar()
nStimsVar.set(mainStruct["nStims"])
ttk.Label(window, text="Number of Stim. in series").grid(column=0, row=row)
ttk.Spinbox(window, from_=0, to=100, width=5,textvariable=nStimsVar).grid(column=1, row=row)

row+=1
nRepeatsVar=IntVar()
nRepeatsVar.set(mainStruct["nRepeats"])
ttk.Label(window, text="Number series repeats").grid(column=0, row=row)
ttk.Spinbox(window, from_=0, to=100, width=5,textvariable=nRepeatsVar).grid(column=1, row=row)

row+=1
stimDurVar=DoubleVar()
stimDurVar.set(mainStruct["stimDur"])
ttk.Label(window, text="Stimulus Duration (ms)").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=stimDurVar).grid(column=1, row=row)

row+=1
isiVar=DoubleVar()
isiVar.set(mainStruct["isi"])
ttk.Label(window, text="InterStimulus Interval (s)").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=isiVar).grid(column=1, row=row)

row+=1
trainPulsesVar=IntVar()
trainPulsesVar.set(mainStruct["trainPulses"])
ttk.Label(window, text="Train n pulses").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=trainPulsesVar).grid(column=1, row=row)

row+=1
trainFreqVar=DoubleVar()
trainFreqVar.set(mainStruct["trainFreq"])
ttk.Label(window, text="Train Freq.(Hz)").grid(column=0, row=row)
ttk.Entry(window,width=5,textvariable=trainFreqVar).grid(column=1, row=row)

row+=1
projectVar=StringVar()
ttk.Label(window, text="Project Title").grid(column=0, row=row)
ttk.Entry(window,width=10,textvariable=projectVar).grid(column=1, row=row)

row+=1
memoVar=StringVar()
ttk.Label(window, text="Memo").grid(column=0, row=row)
ttk.Entry(window,width=10,textvariable=memoVar).grid(column=1, row=row)

row+=1
mouseVar=IntVar()
mouseVar.set(1)
ttk.Label(window, text="Mouse #").grid(column=0, row=row)
ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=mouseVar).grid(column=1,row=row)

row+=1
sliceVar=IntVar()
sliceVar.set(1)
ttk.Label(window, text="Slice #").grid(column=0, row=row)
ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=sliceVar).grid(column=1,row=row)

row+=1
trialVar=IntVar()
trialVar.set(1)
ttk.Label(window, text="Trial #").grid(column=0, row=row)
ttk.Spinbox(window, from_=1, to=10, width=5,textvariable=trialVar).grid(column=1,row=row)

row+=1
previewModeVar=IntVar()
previewModeVar.set(1)
ttk.Checkbutton(window, text="Preview Mode",variable=previewModeVar).grid(column=0, row=row)
bipolarVar=BooleanVar()
bipolarVar.set(True)
bipolarCheck = ttk.Checkbutton(window,text="Bipolar",variable=bipolarVar)
bipolarCheck.grid(column=1,row=row)
bipolarCheck.state(["selected"])

row+=1
logStepsVar=BooleanVar()
logStepsVar.set(mainStruct["logSteps"])
ttk.Checkbutton(window,text="LogSteps",variable=logStepsVar).grid(column=0,row=row)

row+=1
ttk.Button(window, text='CloseFig', command=closeAllFigures).grid(column=0,row=row)
ttk.Button(window,text="Files",command=lambda:showWindow(fileWindow)).grid(column=1,row=row)

row+=1
ttk.Button(window, text="Plot Menu",command=lambda:showWindow(plotWindow)).grid(column=0, row=row)
ttk.Button(window,text="Mouse Menu",command=lambda:showWindow(mouseWindow)).grid(column=1,row=row)

row+=2
recordBtn = ttk.Button(window, text="START", command=onRecordClick)
recordBtn.grid(columnspan=2,row=row,padx=1)
runStatusLabel = ttk.Label(window, text='idle', font='Arial 8 bold')
runStatusLabel.grid(column=1, row=row)

row+=11
logText = scrolledtext.ScrolledText(window,width=30,height=2)
logText.grid(columnspan=2,row=row,padx=15)
clock()

row+=1
ttk.Button(window, text="EXIT", command=exitController).grid(columnspan=2,row=row,padx=1)


#################File window#########################################

row=1  # rows start over in each window
fileWindow.title("Parameter File")
ttk.Button(fileWindow, text="Open File", command=openParamsFile).grid(row=row,pady=5,padx=5)
row+=1
ttk.Button(fileWindow, text="Save File", command=saveParamsFile).grid(row=row,pady=5,padx=5)
row+=1
ttk.Button(fileWindow, text="OK", command=lambda:hideWindow(fileWindow)).grid(row=row,pady=5,padx=5)


#################Mouse window#########################################

row=0
mouseWindow.title("Mouse choice")
tk.Label(mouseWindow, text = "Which Mouse will you use today?",font='Arial 11 bold').grid(row=row,pady=5,padx=2)
row+=2
todaysMice=getTodaysMice()
projects=getProjects()
mouseCombo = ttk.Combobox(mouseWindow, values=[],width=50)
if todaysMice:
   mouseChoices=[]
   for curMouse in todaysMice:
       # need to put in a strain so that tdt code doesn't choke
       if len(curMouse[2])<1:
           strain="empty"
       else:
           strain=list(curMouse[2])[0]
       mouseDesc='None'
       if type(curMouse) is tuple:
           age=curMouse[6]-date.today()
           mouseAge='p'+str(abs(age.days))
           mouseDesc='Strain:{:s} ID/eartag:{:d}/{:d} {:s}{:s} {:s}'.format(strain,curMouse[0],curMouse[3], mouseAge,curMouse[4],curMouse[8])
       mouseChoices.append(mouseDesc)
   mouseCombo.config(values=mouseChoices)
   mouseCombo.current(len(mouseChoices)-1) # default to the last mouse
   mouseCombo.grid(row=row,pady=5)
   row+=1
if projects:
    tk.Label(mouseWindow, text = "Which Project will you use today?",font='Arial 11 bold').grid(row=row,pady=5,padx=2)
    row+=2
    projectChoices=[project[0] for project in projects]
    projectCombo = ttk.Combobox(mouseWindow, values=projectChoices,width=30)
    projectCombo.current(len(projectChoices)-1) # default to the last project
    projectCombo.grid(row=row,pady=5)

row+=1
ttk.Button(mouseWindow, text="OK", command=acceptMouseChoice).grid(row=row,pady=5)

##################Plot Window######
row=1  # rows start over in each window
plotWindow.title("Plot Parameters")

baselineOffsetVar=BooleanVar()
baselineOffsetVar.set(mainStruct["baselineOffset"])
ttk.Checkbutton(plotWindow, text="Baseline Offset",variable=baselineOffsetVar).grid(column=0, row=row,columnspan=4)

row+=1
plotLFPVar=BooleanVar()
plotLFPVar.set(mainStruct["doLFP"])
ttk.Checkbutton(plotWindow, text="Plot LFP",variable=plotLFPVar).grid(column = 1, row=row)
gainLFPVar=DoubleVar()
gainLFPVar.set(mainStruct["gainLFP"])
ttk.Label(plotWindow, text="Gain LFP" ).grid(column=2, row=row)
ttk.Entry(plotWindow,width=5,textvariable=gainLFPVar).grid(column=3, row=row)

row+=1
plotCSDVar=BooleanVar()
plotCSDVar.set(mainStruct["doCSD"])
ttk.Checkbutton(plotWindow, text="Plot CSD", variable=plotCSDVar).grid(column=1, row=row)
gainCSDVar=DoubleVar()
gainCSDVar.set(mainStruct["gainCSD"])
ttk.Label(plotWindow, text="Gain CSD").grid(column=2, row=row)
ttk.Entry(plotWindow,width=5,textvariable=gainCSDVar).grid(column=3, row=row)

row+=1
# table title row
for column,title in enumerate(["","Channel","Begin (ms)","End (ms)"]):
    ttk.Label(plotWindow, text=title).grid(column=column, row=row)

row+=1
# display window around the stim
preStimTimeVar=DoubleVar()
preStimTimeVar.set(mainStruct["preStimTime"])
ttk.Label(plotWindow, text="Display").grid(column=0, row=row)
ttk.Entry(plotWindow,width=5,textvariable=preStimTimeVar).grid(column=2, row=row)
postStimTimeVar=DoubleVar()
postStimTimeVar.set(mainStruct["postStimTime"])
ttk.Entry(plotWindow,width=5,textvariable=postStimTimeVar).grid(column=3, row=row)

# this row is the first channel to measure
row+=1
channelAVar=IntVar()
channelAVar.set(mainStruct["plotChannelA"])
ttk.Label(plotWindow, text="Meas. A").grid(column=0, row=row)
ttk.Entry(plotWindow,width=5,textvariable=channelAVar).grid(column=1,row=row)
measure1BeginVar=DoubleVar()
measure1BeginVar.set(mainStruct["measure1Begin"])
ttk.Entry(plotWindow,width=5,textvariable=measure1BeginVar).grid(column=2, row=row)
measure1EndVar=DoubleVar()
measure1EndVar.set(mainStruct["measure1End"])
ttk.Entry(plotWindow,width=5,textvariable=measure1EndVar).grid(column=3, row=row)

# this row is the second channel to measure
row+=1
channelBVar=IntVar()
channelBVar.set(mainStruct["plotChannelB"])
ttk.Label(plotWindow, text="Meas. B").grid(column=0, row=row)
ttk.Entry(plotWindow,width=5,textvariable=channelBVar).grid(column=1,row=row)
measure2BeginVar=DoubleVar()
measure2BeginVar.set(mainStruct["measure2Begin"])
ttk.Entry(plotWindow,width=5,textvariable=measure2BeginVar).grid(column=2, row=row)
measure2EndVar=DoubleVar()
measure2EndVar.set(mainStruct["measure2End"])
ttk.Entry(plotWindow,width=5,textvariable=measure2EndVar).grid(column=3, row=row)

row+=1
ttk.Button(plotWindow, text="OK", command=lambda:hideWindow(plotWindow)).grid(columnspan=4,row=row,padx=1)
#########

window.mainloop()
