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

print(exchange.addFunds(userId, 'rur', 2000))
print(exchange.users)

print(exchange.addFunds(userId, 'rur', 20))
print(exchange.users)

print(exchange.addFunds(userId, 'btc', 0.01))
print(exchange.users)

print(exchange.addFunds(userId, 'btc', 0.0005))
print(exchange.users)

print("Проверка скриптов во время разработки окончена")

from misc import ceil, StrToTS


#print(ceil(1239.92347, -1))