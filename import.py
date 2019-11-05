#!/usr/bin/env python
#-*-coding:utf-8-*-

pairId = 16# 11 btc/rur exmo

CONFIG_FILE_NAME = 'config.json'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

import json
cfgFileName = dirName + os.path.sep + CONFIG_FILE_NAME
if not os.path.isfile(cfgFileName):
	print('create config file in json format with name "config.json"')
	exit()

file = open(cfgFileName, 'r+')
config = json.load(file)
file.close()
if not 'external_db' in config:
	print('create external_db in config file')
	exit()

externalDbConfig = config['external_db']

from externaldata import ExternalData

datasource = ExternalData(**externalDbConfig)
if not datasource.hasPairStatistic(pairId):
	print('Data Source not has statistic for pairId: ' + str(pairId))
	exit()

DB_DIR = 'db'
DB_NAME = 'database.db'
dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME

from localdata import LocalData

print("start import")
datadest = LocalData(dbFileName, pairId)
datadest.addPairStatistic(datasource.getPairStatistic(pairId))
print("complete import")
