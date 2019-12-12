#!/usr/bin/env python
#-*-coding:utf-8-*-

import MySQLdb

class ExternalData:
	connect = None
	
	def __init__(self, host = None, db = None, user = None, pswd = None, port = 3306):
		self.connect = MySQLdb.connect(
			host = host,
			user = user,
			passwd = pswd,
			db = db,
			port = port,
			charset = 'utf8',
			use_unicode = True)

	def hasPairStatistic(self, pairId = None):
		if not type(pairId) is int:
			return False
		
		query = """
			SELECT COUNT(*) cou
			FROM s_trade_stats
			WHERE pair_id = {0}
		""".format(pairId)

		cursor = self.connect.cursor()

		cursor.execute(query)
		rows = cursor.fetchall()

		if len(rows) <= 0:
			return False
		
		if rows[0][0] > 0:
			return True
		
		return False

	def getPairStatistic(self, pairId = None):
		if not type(pairId) is int:
			return False
		
		query = """
			SELECT *
			FROM s_trade_stats
			WHERE pair_id = {0}
		""".format(pairId)

		cursor = self.connect.cursor()

		cursor.execute(query)
		return cursor.fetchall()
	
	def getMinAndMaxStartTS(self, pairId):
		""" get min and max start TS for specified TS """
		query = """
			SELECT 
				MIN(start_ts) as min_start_ts,
				MAX(start_ts) as max_start_ts
			FROM 
				s_trade_stats
			WHERE
				pair_id = {0}
		""".format(pairId)
		
		cursor = self.connect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()

	def __del__(self):
		self.connect.close()
