#!/usr/bin/env python
#-*-coding:utf-8-*-

CONFIG_FILE_NAME = 'test_trade.json'
CONFIG_FOLDER_NAME = 'configs'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))
import json

def get_config(key = ""):
	""" загружаем файл конфигурации """
	config_file_path = dirName + os.path.sep + '..' + os.path.sep + '..' + os.path.sep + CONFIG_FOLDER_NAME + os.path.sep + CONFIG_FILE_NAME
	if not os.path.isfile(config_file_path):
		raise Exception("Не найден файл конфигурации \"%s\"" % config_file_path)
	
	config_file = open(config_file_path, 'r+')
	configs = json.load(config_file)
	config_file.close()

	if key in configs:
		return configs[key]

	return {}
