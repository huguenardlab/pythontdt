
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import Text
from tkinter import *
#from micedb import *
from plotLFP import *
from plotCSD import *
from offset_baseline import *
import tkinter as tk
import sys
import os
import shutil
import time
import collections
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

def clickrecord():
   # make minor change here to test git update
    global run
    global stim
    global isiT
    global inival
    global stepval
    global nr
    global ns
    global recording
    global block
    global project
    global memoNote
    global mouseNb
    global sliceNb
    global trial
    global blockStore
    
    if recording :
     recording=0   
     record["text"]= "Start"
     run=1000
     stim=1000
     
     onestim()
    else :
        #Creation of a new directory
        #parent_dir='D:/TDTdata' 
        #directory=prjt.get()  #will use Projet to create the new 'file'
        #window.directoryname = os.path.join(parent_dir, directory)
        window.directoryname='D:/TDTdata'
       
        print(window.directoryname)
    
        NewTank=ttank.AddTank(d,'REGISTER@'+window.directoryname)
    
        if NewTank:
           print('New Tank Added: '+window.directoryname)
           newtankmessage='New Tank Added: '+window.directoryname
        else:
            print('ERROR! New Tank '+window.directoryname+' was not added.')
            window.destroy()
            sys.exit()

        NewTank=ttank.AddTank(d,'REGISTER@'+window.directoryname)

        NewTankName=tdt.SetTankName(window.directoryname.replace('/','\\')+'\\'+d)
        print(NewTankName)
        
        if NewTankName:
            print('New Tank Name: '+window.directoryname.replace('/','\\')+'\\'+d)
            newtanknamemessage='\nNew Tank Name: '+window.directoryname.replace('/','\\')+'\\'+d
        else:
            print('ERROR! Could not name new tank '+window.directoryname.replace('/','\\')+'\\'+d)
            window.destroy()
            sys.exit()

        print('tank set name return value = ',NewTankName)
        #print(tdt.GetTankName())
        
       
        tdt.SetTargetVal('Rec16Cha.BipolarStim',Bipolar.get())
        tdt.SetTargetVal('Rec16Cha.StimDuration',stimdur.get())
        #print (tdt.GetTargetVal('Rec16Cha.BipolarStim'))
        recording=1
        if PreviewMode.get():
            mode=2
        else:
            mode=3      
        tdt.SetSysMode(mode)
        time.sleep(1) 
        record["text"]= "Stop"
        nr=nrep.get()
        ns=nstim.get()
        inival=initv.get()
        stepval=stepv.get()
        isiT=isi.get()
        run=1
        stim=0
        ttank.OpenTank(d,'R')
        block=ttank.GetHotBlock()
        onestim()

def clock():
    global laststimtime
    t=time.strftime('%I:%M:%S %p',time.localtime())+'{: 4.0f}'.format(time.time()-laststimtime) 
    if t!='':
        lblt.config(text=t)
    window.after(1000,clock)

#Exit TDT properly
def exitTDT():
    print ('Exit has been pressed')
    tankCheck=ttank.CheckTank(d)
    #print(tankCheck)
    ttank.CloseTank()
    #print(tankCheck)
    tdt.CloseConnection()
    #print(tdt.CheckServerConnection())
    ttank.ReleaseServer()
    window.destroy()
    sys.exit()
    

#trigger the stim, create and store Notes
def onestim() :
    global run
    global stim
    global isiT
    global inival
    global stepval
    global nr
    global ns
    global laststimtime
    global project
    global block
    global memoNote
    global mouseNb
    global sliceNb
    global trialNb
    global initvNb
    global stepvNb
    global nstimNb
    global nrepNb
    global stimdurNb
    global isiNb
    global bipolarNb
    global curRun
    global curStim
    global sweep
    global blockStore
    global todaymice
    if run<=nr :
      if stim<ns :
        stim+=1
        thisStim=inival+ (stim-1)*stepval
        lblrunstatus.config(text='Run '+str(run)+' Stim '+str(stim)+'{: .1f}'.format(thisStim)+'V')
        curRun=str(run)
        curStim=str(stim)
        # send out current stimulus value
        tdt.SetTargetVal('Rec16Cha.SingleStimValue',thisStim)
        tdt.SetTargetVal('Rec16Cha.StimEnable',1)
        tdt.SetTargetVal('Rec16Cha.StimDuration',stimdur.get())
        tdt.SetTargetVal('Rec16Cha.BipolarStim',Bipolar.get())
        # trigger a sweep with a rising edge signal
        tdt.SetTargetVal('Rec16Cha.SingleStimTrigger',1)
        # reset SingleStimTrigger value to 0, so that it can be triggered next time
        # the assumption is that the trigger has actually already been detected.
        tdt.SetTargetVal('Rec16Cha.SingleStimTrigger',0)
        laststimtime=time.time()
        window.after(int(isiT*1000),onestim)
        
           #LFP display online
        
        ttank.OpenTank(d,'R')#do it only first time
        
        block=ttank.GetHotBlock()
        ttank.SelectBlock(block)
        expectedsweeps=((run-1)*ns+stim)*16
        sweepobtained=0
        while not sweepobtained:
          N = ttank.ReadEventsSimple('SSwp')
          data = ttank.ParseEvV(0, N)
          npdata = np.array(data)
          #print( np.shape(npdata))
          thissweep=[]
          if np.size(npdata)>1:
            if np.shape(npdata)[1]==expectedsweeps:
              sweepobtained=1
              npdatashape=np.shape(npdata)
              lastcolumn=npdatashape[1]
              firstcolumn=lastcolumn-16
              thissweep=npdata[:,firstcolumn:lastcolumn]
              newrange=range(15,0,-1)
              newrange=np.insert(newrange,0,0)
              #print(newrange)
              thissweep=thissweep[:,newrange]
              
              
        #baseline offset
        if baselineOffset.get()==1:
            thissweep=offsetTDT(thissweep)
        
        #plot the LFP
        if plotMode.get()==1:
            
            plotTDTdata(thissweep,0.006,plotstruct)
            
        #plot the CSD
        if plotModeCSD.get()==1:
            
            plotCSDdata(thissweep,0.006,plotstructCSD)
        
        
        
      else :
        run+=1
        stim=0
        onestim()
    else :
      ttank.OpenTank(d,'R')
      ttank.SelectBlock(block)
      project='Project: '+prjt.get()
      memoNote='Memo: '+ memo.get()
      mouseNb='Mouse: '+str(mouse.get())
      sliceNb='Slice: '+str(slice.get())
      trialNb='Trial: '+str(exp.get())
      initvNb='Initial stim intensity: '+ str(initv.get())+'V'
      stepvNb='Stim increment:'+ str(stepv.get())+'V'
      nstimNb= 'Number of stim in the series: '+ str(nstim.get())
      nrepNb='Number of series repetitions: '+str(nrep.get())
      stimdurNb='Stim duration: ' + str (stimdur.get())+'ms'
      isiNb= 'Stim interval: '+str(isi.get())+'s'
      if Bipolar.get()==1:
        bipolarNb='Bipolar stimulation'
      else:
        bipolarNb='Monopolar stimulation'  
      state='Interrupt after: '+curRun+' of '+ str(nrep.get()) + ' Runs and after '+ curStim+' of '+ str(nstim.get()) +' Stims of this Run'
      allnote='Date: '+d+', '+'Block: '+block+', '+memoNote+', '+mouseNb+', '+sliceNb+', '+trialNb 
      stimparam= initvNb+', '+stepvNb+', '+nstimNb+', '+nrepNb+', '+stimdurNb+', '+isiNb+ ', '+bipolarNb
      ttank.AppendNote(project)
      ttank.AppendNote(allnote)
      ttank.AppendNote(stimparam)
      ttank.AppendNote(state)
      print(ttank.GetNote(1))
      print(ttank.GetNote(2))
      print(ttank.GetNote(3))
      print(ttank.GetNote(4))
      stimbuffer.insert(INSERT,'\n'+project)
#      stimbuffer.insert(INSERT,'\n'+blockStore)
      stimbuffer.insert(INSERT,'\n'+allnote)
      stimbuffer.insert(INSERT,'\n'+stimparam)

      tdt.SetSysMode(0)
      lblrunstatus.config(text='Idle')
      record["text"]= "Start"

recording=0
laststimtime=time.time()
try:
    import win32com.client
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

if ttank.ConnectServer('Local','Me') !=1:
    sys.exit('could not connect to Tank')
if tdt.ConnectServer('Local') != 1:
    ttank.CloseTank() # added these three lines to shut down tdt connections on failure, 6/25/20 jrh
    tdt.CloseConnection()
    ttank.ReleaseServer()
    sys.exit('could not connect to Workbench / Synapse')
#if tdt.ConnectServer('Local') != 1:
#    sys.exit('could not connect to Workbench / Synapse')
  #print(tdt.devicstatus)
  #print('tdtdevice 0',tdt.getdevicename(0),'device 1',tdt.getdevicename(1))
    
stimsize=tdt.GetTargetSize('Rec16Cha.StimBuffIn')
deviceName=tdt.GetDeviceName(0)

plotstruct=[0,1,2]  
plotstructCSD=[0,1,2] 
  
print ('stim buffer size = ',stimsize)
print('Device name #0 =',tdt.GetDeviceName(0))
print('Device RCO file =',tdt.GetDeviceRCO(tdt.GetDeviceName(0)))
print('Device status=',tdt.GetDeviceStatus(tdt.GetDeviceName(0)))
if not deviceName:
    sys.exit('TDT lied.  We were not actually connected')

    
window = Tk()

 
d=time.strftime('%Y%m%d',time.localtime())


# Indle mode
tdt.SetSysMode(0)

run=1
stim=0

r=0;
window.title("Python TDT Controller")
window.geometry('300x500')

#lbldn = Label(window, text=window.directoryname)
#lbldn.grid(column=0, row=r,columnspan=2)
#r+=1
# date

lblt = Label(window)
lblt.grid(column=0, row=r)
lbldt = Label(window, text=d)
lbldt.grid(column=1, row=r)

r+=1
buffer= []
initv=DoubleVar()
initv.set(1)
lbl = Label(window, text="Initial Stim Intensity (V)")
lbl.grid(column=0, row=r)
txt = Entry(window,width=5,textvariable=initv)
txt.grid(column=1, row=r)

r+=1
stepv=DoubleVar()
stepv.set(1)
lbl2 = Label(window, text="Stimulus Increment (V)")
lbl2.grid(column=0, row=r)
txt2 = Entry(window,width=5,textvariable=stepv)
txt2.grid(column=1, row=r)

r+=1
nstim=IntVar()
nstim.set(5)
lbl3 = Label(window, text="Number of Stim. in series")
lbl3.grid(column=0, row=r)
numstim = Spinbox(window, from_=0, to=100, width=5,textvariable=nstim)
numstim.grid(column=1, row=r)

r+=1
nrep =IntVar() 
nrep.set(5) 
lbl4 = Label(window, text="Number series repeats")
lbl4.grid(column=0, row=r)
numreps = Spinbox(window, from_=0, to=100, width=5,textvariable=nrep)
numreps.grid(column=1, row=r)

r+=1
stimdur=DoubleVar()
stimdur.set(0.1)
lblsd = Label(window, text="Stimulus Duration (ms)")
lblsd.grid(column=0, row=r)
txtsd = Entry(window,width=5,textvariable=stimdur)
txtsd.grid(column=1, row=r)

r+=1
isi=DoubleVar()
isi.set(15)
lbl = Label(window, text="InterStimulus Interval (s)")
lbl.grid(column=0, row=r)
txt = Entry(window,width=5,textvariable=isi)
txt.grid(column=1, row=r)

#r+=1
#blckstr=StringVar()
#blckstr.set('Tot=100ms; Pre=5ms')
#lblblckstr = Label(window, text="Block store")
#lblblckstr.grid(column=0, row=r)
#txtblckstr = Label (window,textvariable=blckstr)
#txtblckstr.place(width=10,height=5)
#txtblckstr.grid(column=1, row=r)

r+=1
prjt=StringVar()
lblproj = Label(window, text="Project Title")
lblproj.grid(column=0, row=r)
txtproj = Entry(window,width=10,textvariable=prjt)
txtproj.grid(column=1, row=r)

r+=1
memo=StringVar()
lblmemo = Label(window, text="Memo")
lblmemo.grid(column=0, row=r)
txtmemo = Entry(window,width=10,textvariable=memo)
txtmemo.grid(column=1, row=r)


r+=1
mouse=IntVar()
mouse.set(1)
lblm = Label(window, text="Mouse #")
lblm.grid(column=0, row=r)
mice = Spinbox(window, from_=1, to=10, width=5,textvariable=mouse)
mice.grid(column=1,row=r)

r+=1
slice=IntVar()
slice.set(1)
lbls = Label(window, text="Slice #")
lbls.grid(column=0, row=r)
slices = Spinbox(window, from_=1, to=10, width=5,textvariable=slice)
slices.grid(column=1,row=r)

r+=1
exp=IntVar()
exp.set(1)
lble = Label(window, text="Trial #")
lble.grid(column=0, row=r)
exps = Spinbox(window, from_=1, to=10, width=5,textvariable=exp)
exps.grid(column=1,row=r)

PreviewMode= IntVar()
PreviewMode.set(1)
previewBtn = Checkbutton(window, text="Preview Mode",variable=PreviewMode)
previewBtn.grid(column=0, row=r)

r+=1
Bipolar= IntVar()
Bipolar.set(1)
ckbtn = Checkbutton(window,text="Bipolar",variable=Bipolar)
ckbtn.grid(column=0,row=r)
r+=1
baselineOffset= IntVar()
baselineOffset.set(0)
offsetBtn = Checkbutton(window, text="Baseline Offset",variable=baselineOffset)
offsetBtn.grid(column=0, row=r)

plotMode= IntVar()
plotMode.set(0)
plotBtn = Checkbutton(window, text="Plot LFP",variable=plotMode)
plotBtn.grid(column=1, row=r)


r+=1
plotModeCSD= IntVar()
plotModeCSD.set(0)
plotCSDBtn = Checkbutton(window, text="Plot CSD",variable=plotModeCSD)
plotCSDBtn.grid(column=1, row=r)



r+=1
record= IntVar()
btn_text = StringVar()
record = Button(window, text="Start", command=clickrecord, bg = "blue", fg= "white")
record.grid(column=0, row=r)

r+=1
Exit= IntVar()
btn_text = StringVar()
Exit = Button(window, text="Exit", command=exitTDT, bg = "red", fg= "white")
Exit.grid(column=0, row=r)

lblrunstatus = Label(window, text='idle')
lblrunstatus.grid(column=1, row=r)

stimbuffer = scrolledtext.ScrolledText(window,width=30,height=5)
r+=2
stimbuffer.grid(columnspan=2,row=r,padx=15)
clock()
if recording:
    stimbuffer.insert(INSERT,newtankmessage)
    stimbuffer.insert(INSERT,newtanknamemessage)


window.mainloop()
