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

def TStoStr(ts = 0, format = "%Y.%m.%d %H:%M:%S"):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
	return int(time.mktime(time.strptime(strTime, format)))

a ={1: 'a', 2: 'b', 3: 'c'}
b ={3: 'ff', 4: 'ee'}

print(a)
print(b)
a.update(b)
print(a)
exit()

query = """
	select min(start_ts) min_ts, max(start_ts) max_ts
	FROM s_trade_stats
	where pair_id = 13
"""
cursor = connection.cursor()

cursor.execute(query)
rows = cursor.fetchall()
print('has data from ' + TStoStr(rows[0][0]) + ' to ' + TStoStr(rows[0][1]))

connection.close()

print((31 / int(10)) * 10)

from localdata import LocalData
pairId = 13
datasource = LocalData(dbFileName, pairId)
print(datasource.getTrades(StrToTS('2019.09.01 00:00:00'), StrToTS('2019.09.01 23:59:59'), 3600, 13))