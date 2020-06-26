#Gabrielle 20200623
#Exit TDT small function


def exitTDT():
    
    print ('exit has been pressed')
    tdt.CloseConnection()
    ttank.ReleaseServer()
    window.destroy()
    sys.exit()
    