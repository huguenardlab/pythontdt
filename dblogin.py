# dblogin.py
# connect to the lab database with the login in db_login.ini, which sits next
# to this file and is not in git (copy db_login_example.ini to make it)

import configparser
import os
import mysql.connector

loginFile=os.path.join(os.path.dirname(os.path.abspath(__file__)),'db_login.ini')

def connectLab():
    login=configparser.ConfigParser(interpolation=None) # a % in the password is literal
    if not login.read(loginFile):
        raise FileNotFoundError('database login file not found: '+loginFile+
            ' (copy db_login_example.ini to db_login.ini and fill it in)')
    db=login['lab']
    return mysql.connector.connect(
        host=db['host'],
        database=db['database'],
        user=db['user'],
        password=db['password'])
