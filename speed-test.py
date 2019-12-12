#!/usr/bin/env python
#-*-coding:utf-8-*-
""" тест скорости выполнения """

import Tkinter as tk
import time
import math

def TStoStr(ts = 0, format = "%Y.%m.%d %H:%M:%S"):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
	return int(time.mktime(time.strptime(strTime, format)))

from localdata import LocalData

DB_DIR = 'db'
DB_NAME = 'database.db'
CONFIG_FILE_NAME = 'config.json'

import json
import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME
cfgFileName = dirName + os.path.sep + CONFIG_FILE_NAME

pairId = 11 # BTC/RUR on exmo.me
#16 BTC/RUR on YoBit
#18 LTC/BTC on YoBit

startTS = time.time()
SQLiteDataSource = LocalData(dbFileName, pairId)
curTS = time.time()
print('connect duration: {0}'.format(curTS - startTS))

file = open(cfgFileName, 'r+')
config = json.load(file)
file.close()
externalDbConfig = config['external_db']
from externaldata import ExternalData
MySQLDataSource = ExternalData(**externalDbConfig)

startTS = time.time()
tradeStartTS, tradeEndTS = MySQLDataSource.getMinAndMaxStartTS(pairId)[0]
curTS = time.time()
print('MySQL stat')
print('min and max values: {0}, connect duration: {1}'.format((TStoStr(tradeStartTS), TStoStr(tradeEndTS)), curTS - startTS))

startTS = time.time()
tradeStartTS, tradeEndTS = SQLiteDataSource.getMinAndMaxStartTS(pairId)[0]
curTS = time.time()
print('SQLite stat')
print('min and max values: {0}, connect duration: {1}'.format((TStoStr(tradeStartTS), TStoStr(tradeEndTS)), curTS - startTS))
