#!/usr/bin/env python
#-*-coding:utf-8-*-
""" test in developer process """

print("Проверка скриптов во время разработки")
CONFIG_FILE_NAME = 'config.json'

import os
import json
from externaldata import ExternalData
from exchange import Exchange
from evo import Evo

from misc import ceil, StrToTS

dirName, fileName = os.path.split(os.path.abspath(__file__))
configFileName = dirName + os.path.sep + CONFIG_FILE_NAME

if os.path.isfile(configFileName):
	paramsFile = open(configFileName, 'r+')
	configParams = json.load(paramsFile)
	paramsFile.close()
else:
	print("Config file not found in {0}".format(configFileName))

if not 'external_db' in configParams:
    print('Section "external_db" not found in {0}'.format(configFileName))
    exit()

dataSource = ExternalData(**configParams['external_db'])

exchange = Exchange(dataSource)

userId = exchange.register()

print("user ID: {0}".format(userId))

print(exchange.users)

print(exchange.addFunds(userId, 'rur', 41))

print(exchange.users)

exchange.setTS(StrToTS("2020.03.14 00:00:00"))

print(exchange.createOrder(userId, 24, "buy", 1, 40))

print(exchange.users)
print(exchange.orders)
print(exchange.reserves)

#print(exchange.isInvestFeeByPairId(24))
#print(exchange.isInvestFeeByPairId(25))

print("Проверка скриптов во время разработки окончена")




#print(ceil(1239.92347, -1))