#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Run evolution test """

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

evolution = Evo(dataSource)

if not 'evo' in configParams:
    print('Section "evo" not found in {0}'.format(configFileName))
    exit()

evolution.init(**configParams['evo'])

evolution.run()

evolution.report()