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
botsInGeneration = 2

startTS = StrToTS("2019.04.01 00:00:00")
endTS = StrToTS("2019.04.10 00:00:00")
stopTS = StrToTS("2019.04.15 00:00:00")

from exchange import Exchange
from bot import Bot
from bot.mutate import Mutate

# ============== init bot arrays ==============
bots = []
curExch = Exchange(datasource, pairId)
for cou in range(botsInGeneration):
	bots.append({'bot': Bot(curExch, pairId)})
mutate = Mutate()

# ============== init bot params ==============
for bot in bots:
	template = bot['bot'].getParamsTemplate()
	bot['params'] = mutate.getRandomParams(template)

# ============== start here ==============
ts = startTS
curExch.reset()
curExch.setTS(ts)

# ============== set bot params ==============
for bot in bots:
	bot['status'] = None
	bot['tradeStatus'] = None
	bot['bot'].reset()
	bot['bot'].init(**bot['params'])
	bot['bot'].setTS(ts)
	bot['startBalance'] = bot['bot'].getBalance()

inWork = True
while inWork:
	ts += 1200
	curExch.setTS(ts)
	for bot in bots:
		bot['bot'].setTS(ts)

	lastPrice = str(curExch.getLastPrice())

	for bot in bots:
		if bot['status'] <> bot['bot'].getStatus():
			print("bot #{0} change status to {1} at {2} last price: {3}".format(bot['bot'].getId(), bot['bot'].getStatus(), TStoStr(ts), lastPrice))
			bot['status'] = bot['bot'].getStatus()

	for bot in bots:
		if bot['tradeStatus'] <> bot['bot'].getTradeStatus():
			print("bot #{0} change trade status to {1} at {2} last price: {3}".format(bot['bot'].getId(), bot['bot'].getTradeStatus(), TStoStr(ts), lastPrice))
			bot['tradeStatus'] = bot['bot'].getTradeStatus()

	# ================ off autorepeat ================ #
	if ts > endTS:
		for bot in bots:
			bot['bot'].setAutorepeat(False)
	# ================ off autorepeat ================ #

	if ts > stopTS:
		for bot in bots:
			if bot['status'] <> 'stopped':
				bot['bot'].stop()


	inWork = False
	for bot in bots:
		if bot['status'] <> 'stopped':
			inWork = True

	print(TStoStr(ts))

print("start date: {0}, end date: {1}\r\n".format(TStoStr(startTS), TStoStr(endTS)))

for bot in bots:
	profitPercent = round((bot['bot'].getBalance() - bot['startBalance']) / bot['startBalance'] * 100, 2)
	print(bot['bot'].getParams())
	print("bot #{0} start balance: {1}, end balance: {2}, profit: {3}%, complete date: {4}\r\n".format(bot['bot'].getId(), bot['startBalance'], bot['bot'].getBalance(), profitPercent, TStoStr(bot['bot'].getChangeStatusTS())))

# sorted(self.items, key = lambda player: player.y) - пример сортировки

exit()