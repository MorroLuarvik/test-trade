#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Stand alone code for test any thihgs """

DB_DIR = 'db'
DB_NAME = 'database.db'

CONFIG_FILE_NAME = 'config.json'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

import sqlite3

print('Hello from here')
dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME
connection = sqlite3.connect(dbFileName)

import time

def TStoStr(ts = 0, format = '%Y.%m.%d %H:%M:%S'):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = 0, format = '%Y.%m.%d %H:%M:%S'):
	return int(time.mktime(time.strptime(strTime, format)))

#TSTime = int(time.time()) # current timestamp

TSTime = 1567260000
strTime = "2019.09.01 00:00:00"

print(TSTime)
print(strTime)
print(StrToTS(strTime))
print(TStoStr(TSTime))

connection.close()