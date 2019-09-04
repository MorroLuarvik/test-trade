#!/usr/bin/env python
#-*-coding:utf-8-*-

from externaldata import ExternalData
#from localbase import localBase

pairId = 13 # ltc/btc exmo

"""
DB_DIR = 'db'
DB_NAME = 'database.db'
"""

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

externalBbConfig = config['external_db']

datasource = ExternalData(**externalBbConfig)
if not datasource.hasPairStatistic(pairId):
	print('Data Source not has statistic for pairId: ' + str(pairId))
	exit()

print("continue")