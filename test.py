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


ts = StrToTS("2018.05.01 00:00:00")

def ceil(i, n):
	return int(i * 10 ** n) / float(10 ** n)

from exchange import Exchange
from bot import Bot
curExch = Exchange(datasource, pairId)
bot = Bot(curExch, pairId)
curExch.setTS(ts)

bot.init()
print(curExch.users)
bot.setTS(ts)

for i in range(4000):
	ts += 1200
	curExch.setTS(ts)
	bot.setTS(ts)

	print(TStoStr(ts) + ' last price ' + str(curExch.getLastPrice()))
	print(curExch.users)
	print(bot.curBot.status)
	print(bot.curBot.cascadeStruct)

exit()


print("last price: " + str(curExch.getLastPrice()))

user1 = curExch.register()
curExch.addFunds(user1, 0.02)

print("start balance: " + str(curExch.getTotalBalance(user1)))

o = curExch.createOrder(user1, "buy", 0.1, 0.016)
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


o = curExch.createOrder(user1, "sell", 0.0998, 0.0172)
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