#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Stand alone code for test any thihgs """

DB_DIR = 'db'
DB_NAME = 'database.db'

CONFIG_FILE_NAME = 'config.json'

import os
dirName, fileName = os.path.split(os.path.abspath(__file__))

import json
cfgFileName = dirName + os.path.sep + CONFIG_FILE_NAME
if os.path.isfile(cfgFileName):
	file = open(cfgFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'host' in config:
		host = config['host']
	if 'db' in config:
		db = config['db']
	if 'user' in config:
		user = config['user']
	if 'pswd' in config:
		pswd = config['pswd']
	if 'port' in config:
		port = config['port']
else:
	print('create config file in json format with name "config.json"')
	exit()

import MySQLdb
connect = MySQLdb.connect(
	host = host,
	user = user,
	port = port,
	passwd = pswd,
	db = db,
	charset = 'utf8',
	use_unicode = True)

connect.close()

#ERROR 2013 (HY000): Lost connection to MySQL server at 'reading initial communication packet', system error: 0

import sqlite3

"""
if (hasData):
	startImport
"""

print('Hello from here')
dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME
connection = sqlite3.connect(dbFileName)

connection.close()