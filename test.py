#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Stand alone code for test any thihgs """

DB_DIR = 'db'
DB_NAME = 'database.db'

CONFIG_FILE_NAME = 'config.json'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

print('Hello from here')
dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME

import time

def TStoStr(ts = 0, format = "%Y.%m.%d %H:%M:%S"):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
	return int(time.mktime(time.strptime(strTime, format)))


from localdata import LocalData
pairId = 13
datasource = LocalData(dbFileName, pairId)
print('sigma: ' + str(datasource.getSigma(StrToTS('2019.09.01 00:00:00'), 30, pairId)))

from exchange import Exchange
curExch = Exchange(datasource, pairId)
curExch.setTS(StrToTS("2018.01.01 00:00:00"))

user1 = curExch.register()
user2 = curExch.register()



curExch.addFunds(user1, 10.0)
curExch.addFunds(user2, 20)

curExch.addFunds(user1, 5)
curExch.addFunds(user2, .5)

print(curExch.users)

o1_1 = curExch.createOrder(user1, "buy", 0.05, 1)
print(curExch.users)
o1_2 = curExch.createOrder(user1, "buy", 0.04, 1)
print(o1_1)

o2_1 = curExch.createOrder(user2, "buy", 0.07, 1)
o2_2 = curExch.createOrder(user2, "buy", 0.06, 1)
print(o2_2)

print(curExch.users)
print(curExch.orders)

print("cancel order " + str(o1_2) + ": " + str(curExch.cancelOrder(user1, o1_2)))

print(curExch.users)
print(curExch.orders)


#print(datasource.getTrades(StrToTS('2019.09.01 00:00:00'), StrToTS('2019.09.01 23:59:59'), 3600, 13))