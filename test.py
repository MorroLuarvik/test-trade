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


startTS = StrToTS("2019.03.01 00:00:00")
checkTS = StrToTS("2019.05.31 00:00:00")
endTS = StrToTS("2019.06.10 00:00:00")

ts = startTS

from exchange import Exchange
from bot import Bot
curExch = Exchange(datasource, pairId)
bot = Bot(curExch, pairId)
curExch.setTS(ts)

bot.init()
bot.setTS(ts)

startBalance = bot.curBot.getBalance()


while ts < endTS:
	ts += 1200
	curExch.setTS(ts)
	bot.setTS(ts)
	
	print(TStoStr(ts) + ' bot status: ' + str(bot.curBot.status) + " " + bot.curBot.getCascadeStatus() + ' last price ' + str(curExch.getLastPrice()))

	if ts > checkTS:
		bot.curBot.autoRepeat = False


print("start date: {0}, check date: {1}, change status date: {2}, end date: {3}".format(TStoStr(startTS), TStoStr(checkTS), TStoStr(bot.curBot.changeStatusTS), TStoStr(endTS)))
profitPercent = round((bot.curBot.getBalance() - startBalance) / startBalance * 100, 2)
print("start balance: {0}, end balance: {1}, profit: {2}%".format(startBalance, bot.curBot.getBalance(), profitPercent))



exit()