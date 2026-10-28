
# dict2file.py
# 9/2/2020
# jrh 
# read or write a simple 1D dictionary from/to file

import csv
import pandas as pd

def writeDict(filename,dict):
  w = csv.writer(open(filename, "w"))
  for key, val in dict.items():
        w.writerow([key, val])

def readDict(filename):
    table=pd.read_csv(filename, header=None, index_col=0)
    return(table.to_dict())


def readDict2(filename):
    DictOut={}
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
           # print(row)
           if row: 
               DictOut[row[0]] = row[1]
    return(DictOut)
