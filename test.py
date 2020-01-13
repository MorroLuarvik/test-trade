#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Stand alone code for test any thihgs """

DB_DIR = 'db'
DB_NAME = 'database.db'

CONFIG_FILE_NAME = 'config.json'
CONF_DIR = 'conf'
LOG_FILE_NAME = 'evo.log'
BOT_PARAMS_FILE = 'bot_params.json'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

print('Hello from here')
dbFileName = dirName + os.path.sep + DB_DIR + os.path.sep + DB_NAME
logFileName = dirName + os.path.sep + CONF_DIR + os.path.sep + LOG_FILE_NAME
botParamsFileName = dirName + os.path.sep + CONF_DIR + os.path.sep + BOT_PARAMS_FILE
configFileName = dirName + os.path.sep + CONFIG_FILE_NAME

import time

def TStoStr(ts = 0, format = "%Y.%m.%d %H:%M:%S"):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
	return int(time.mktime(time.strptime(strTime, format)))

import json
#from localdata import LocalData
from externaldata import ExternalData

pairId = 18

if os.path.isfile(configFileName):
	paramsFile = open(configFileName, 'r+')
	configParams = json.load(paramsFile)
	paramsFile.close()
else:
	print("Config file not found in {0}".format(configFileName))

datasource = ExternalData(**configParams['external_db'])
#datasource = LocalData(dbFileName, pairId)
botsInGeneration = 7
generatons = 32

startTS = StrToTS("2019.11.19 00:00:00") # startTS = StrToTS("2019.04.08 00:00:00")
endTS = StrToTS("2019.12.10 00:00:00") # endTS = StrToTS("2019.11.03 00:00:00")
stopTS = StrToTS("2019.12.11 00:00:00") # stopTS = StrToTS("2019.11.04 00:00:00")
weightParams = {'profitPercent': {'weight': .45}, 'changeStatusCounter': {'weight': .55, 'maxValue': 10}}

from exchange import Exchange
from bot import Bot
from bot.mutate import Mutate

# ============== init bot arrays ==============
bots = []
curExch = Exchange(datasource, pairId)
for cou in range(botsInGeneration):
	bots.append({'bot': Bot(curExch, pairId)})
mutate = Mutate()
mutate.setWeightParams(weightParams)

# ============== init bot params ==============
if os.path.isfile(botParamsFileName):
	paramsFile = open(botParamsFileName, 'r+')
	storedParams = json.load(paramsFile)
	paramsFile.close()
else:
	storedParams = []

idx = 0
for bot in bots:
	template = bot['bot'].getParamsTemplate()
	if len(storedParams) > idx:
		bot['params'] = storedParams[idx]
	else:
		bot['params'] = mutate.getRandomParams(template)
	idx += 1

logFile = open(logFileName, "a+")
logFile.write("start date: {0}, end date: {1}, stop date: {2}\r\n".format(TStoStr(startTS), TStoStr(endTS), TStoStr(stopTS)))
logFile.close()

for generation in range(generatons):
	print("generation# {0}".format(generation))
	# ============== start here ==============
	ts = startTS
	curExch.reset()
	curExch.setTS(ts)

	# ============== set bot params ==============
	for bot in bots:
		bot['status'] = None
		bot['tradeStatus'] = None
		bot['changeStatusCounter'] = 0
		bot['changeStatusTS'] = startTS
		bot['bot'].reset()
		bot['bot'].init(**bot['params'])
		bot['bot'].setTS(ts)
		bot['startBalance'] = bot['bot'].getBalance()

	inWork = True
	while inWork:
		ts += 1200
		curExch.setTS(ts)

		#print(curExch.orders)
		#print(curExch.users)

		for bot in bots:
			bot['bot'].setTS(ts)

		lastPrice = str(curExch.getLastPrice())

		for bot in bots:
			if bot['status'] <> bot['bot'].getStatus():
				print("bot #{0} change status to {1} at {2} last price: {3}".format(bot['bot'].getId(), bot['bot'].getStatus(), TStoStr(ts), lastPrice))
				bot['status'] = bot['bot'].getStatus()
				if bot['status'] == 'inWork':
					bot['changeStatusCounter'] += 1

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

		print(TStoStr(ts) + "\r"), 

	print("start date: {0}, end date: {1}\r\n".format(TStoStr(startTS), TStoStr(endTS)))
	
	for bot in bots:
		profitPercent = round((bot['bot'].getBalance() - bot['startBalance']) / bot['startBalance'] * 100, 2)
		bot['profitPercent'] = profitPercent
		bot['changeStatusTS'] = bot['bot'].getChangeStatusTS()
		print(bot['bot'].getParams())
		print("bot #{0} start balance: {1}, end balance: {2}, profit: {3}%, complete date: {4}, change status counts: {5} \r\n".format(bot['bot'].getId(), bot['startBalance'], bot['bot'].getBalance(), profitPercent, TStoStr(bot['bot'].getChangeStatusTS()), bot['changeStatusCounter']))
	
	logFile = open(logFileName, "a+")
	logFile.write("generation# {0}\r\n".format(generation))
	
	for bot in bots:
		bot['weight'] = mutate.getWeight(bot, bots)
		logFile.write(json.dumps(bot['bot'].getParams()))
		logFile.write("\nbot #{0} start balance: {1}, end balance: {2}, profit: {3}%, weight: {6}, complete date: {4}, change status counts: {5} \r\n".format(bot['bot'].getId(), bot['startBalance'], bot['bot'].getBalance(), bot['profitPercent'], TStoStr(bot['bot'].getChangeStatusTS()), bot['changeStatusCounter'], bot['weight']))

	logFile.close()

	# =============== arrange params by profit percent =============== #
	sortedParams = []
	for item in sorted(bots, key=lambda item: item['weight'], reverse=True): # TODO change profitPercent 2 weight
		sortedParams.append(item['params'])
	# =============== arrange params by profit percent =============== #

	# =============== fuse and mutate params =============== #
	for idx in xrange(len(sortedParams) / 2):
		template = bots[idx]['bot'].getParamsTemplate()
		sortedParams[-idx - 1] = mutate.mutateParams(template, mutate.fusionParams(template, sortedParams[idx], sortedParams[idx + 1]))
	paramsFile = open(botParamsFileName, 'w+')
	paramsFile.write(json.dumps(sortedParams))
	paramsFile.close()
	# =============== fuse and mutate params =============== #
	
	# =============== set mutated params to bots =============== #
	idx = 0
	for bot in bots:
		bot['params'] = sortedParams[idx]
		idx += 1
	# =============== set mutated params to bots =============== #

exit()