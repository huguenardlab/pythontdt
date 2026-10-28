# micedb.py
# this function will return all database rows for mice with expDay matching today

from datetime import date
from datetime import datetime
from datetime import timedelta
from dblogin import connectLab


def gettodaysmice():
  today = date.today() #-timedelta(days = 1) # would give yesterday
  connect=connectLab()
  cursor=connect.cursor()
  #cursor
  #sql="select * from mousegeno where DOE='" + today.strftime("%Y-%m-%d") + "'"
  #print(sql)
  cursor.execute("select * from mousegeno where DOE='" + today.strftime("%Y-%m-%d") + "' or Experimenting=1")
  results=cursor.fetchall()
  #columnnames=cursor.columnnames() # in case you want these too
  #print(results)
  #print(len(results))
  #if len(results)<1:
  #  print(len(results))
    #results=['None']
  cursor.close()
  connect.close()
  return(results)

def getprojects():
  connect=connectLab()
  cursor=connect.cursor()
  cursor.execute("select Name from projects order by Name");
  results=cursor.fetchall()
  cursor.close()
  connect.close()
  return(results)


def addTrialData(mainStruct):
    connect=connectLab()
    cursor1=connect.cursor()
    date=datetime.fromtimestamp(mainStruct["laststimtime"]).strftime('%Y-%m-%d %H:%M:%S')
    print(date)
    query="INSERT INTO TDTtrials "+\
    "(mouseID, slice, block, memo, initstim, stimincr, "+\
    "numstim, numruns, bipolarstim, stimdur, stiminterval, project,trainNP,trainFreq,trialnum, trialtime)"+\
    "VALUES ('"+str(mainStruct["mouseID"])+"',"+str(mainStruct["slice"])+",'"+str(mainStruct["block"])+\
    "','"+str(mainStruct["memo"])+" - Changes:"+str(mainStruct["allmemo"])+"',"+str(mainStruct["iniVal"])+","+str(mainStruct["stepVal"])\
    +","+str(mainStruct["ns"])+","+str(mainStruct["nr"])+","+str(mainStruct["bipolar"])\
    +","+str(mainStruct["stimDur"])+","+str(mainStruct["isiT"])+",'"\
    +str(mainStruct["project"])+"',"+str(mainStruct["trainNP"])+","+str(mainStruct["trainFreq"])+","\
    +str(mainStruct["trial"])+",'"+str(date)+"')"
   # print(query)
    cursor1.execute(query)
    connect.commit()
    query="SELECT LAST_INSERT_ID()"
    cursor1.execute(query)
    results=cursor1.fetchall()
    cursor1.close()
    connect.close()
    return((results[0][0]))

