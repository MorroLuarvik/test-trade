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
curExch.setTS(StrToTS("2018.05.01 00:00:00"))
print("last price: " + str(curExch.getLastPrice()))

user1 = curExch.register()
curExch.addFunds(user1, 0.02)

print("start balance: " + str(curExch.getTotalBalance(user1)))

o = curExch.createOrder(user1, "buy", 0.016, 0.1)
print("after create buy order")
print("balance: " + str(curExch.getTotalBalance(user1)))
print(curExch.users)
print(curExch.orders)

curExch.setTS(StrToTS("2018.05.13 00:00:00"))
print("after change date")
print("balance: " + str(curExch.getTotalBalance(user1)))
print("last price: " + str(curExch.getLastPrice()))
print(curExch.users)
print(curExch.orders)


o = curExch.createOrder(user1, "sell", 0.0172, 0.0998)
print("after create sell order")
print("balance: " + str(curExch.getTotalBalance(user1)))
print(curExch.users)
print(curExch.orders)

curExch.setTS(StrToTS("2018.05.18 00:00:00"))
print("after change date")
print("balance: " + str(curExch.getTotalBalance(user1)))
print("last price: " + str(curExch.getLastPrice()))
print(curExch.users)
print(curExch.orders)


print("final balance: " + str(curExch.getTotalBalance(user1)))