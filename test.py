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
endTS = StrToTS("2019.03.10 00:00:00")

ts = startTS

from exchange import Exchange
from bot import Bot

bots = []
curExch = Exchange(datasource, pairId)
bots.append({'bot': Bot(curExch, pairId)})
bots.append({'bot': Bot(curExch, pairId)})

curExch.setTS(ts)

sigmaIndent = 0.15
for bot in bots:
	bot['bot'].init(sigmaIndent)
	sigmaIndent = 0.1
	bot['bot'].setTS(ts)
	bot['startBalance'] = bot['bot'].getBalance()
	bot['status'] = None

inWork = True
while inWork:
	ts += 1200
	curExch.setTS(ts)
	for bot in bots:
		bot['bot'].setTS(ts)

	print(TStoStr(ts) + ' last price ' + str(curExch.getLastPrice()))

	for bot in bots:
		if bot['status'] <> bot['bot'].getStatus():
			print("bot #{0} change status to {1}".format(bot['bot'].getId(), bot['bot'].getStatus()))
			bot['status'] = bot['bot'].getStatus()

	if ts > endTS:
		for bot in bots:
			bot['bot'].setAutorepeat(False)

	inWork = False
	for bot in bots:
		if bot['status'] <> 'stopped':
			inWork = True

print("start date: {0}, end date: {1}".format(TStoStr(startTS), TStoStr(endTS)))

for bot in bots:
	profitPercent = round((bot['bot'].getBalance() - bot['startBalance']) / bot['startBalance'] * 100, 2)
	print("bot #{0} start balance: {1}, end balance: {2}, profit: {3}%".format(bot['bot'].getId(), bot['startBalance'], bot['bot'].getBalance(), profitPercent))

exit()