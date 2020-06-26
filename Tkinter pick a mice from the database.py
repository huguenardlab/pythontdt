

from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import Text
from tkinter import *
from micedb import *
import numpy as np
import tkinter as tk

window = Tk()

window.directoryname='D:/TDTdata'

mouseListing=gettodaysmice()

r=0;
window.title("Pick a Mice from the Database")
window.geometry('400x250')


lbldn = Label(window, text=window.directoryname)
lbldn.grid(column=0, row=r,columnspan=2)
r+=1

r+=1
mouseOfTheDay=DoubleVar()
mouseD = Label(window, text="Select your mice")
mouseD.grid(column=0, row=r)
mouseList = Listbox(window, width=50,selectmode=SINGLE)

listShape=np.shape(mouseListing)
numberOfElement=listShape[0]

for i in range ( 0 , numberOfElement):
    mouseList.insert(i,mouseListing[i])
    
mouseList.grid(column=1, row=r)



#get the list from the selected Mice


def OnButtonClick():
    selection = mouseList.curselection()
    print(selection[0])
    curMouse=mouseList.get(selection[0])
    print(curMouse)
    
r+=1
button= IntVar()
btn_text = StringVar()
button= Button(window, text="Start", command= OnButtonClick, bg = "red", fg= "white")
button.grid(column=0, row=r)



#if curMice==1:
  #  MousePar=mouseList.get(curMice)
    #print(MousePar)

window.mainloop()
