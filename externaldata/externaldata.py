#!/usr/bin/env python
#-*-coding:utf-8-*-

import MySQLdb

class ExternalData:
	SEC_ID_DAY = 24 * 3600
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
	
	def getPriceStat(self, startTS, endTS, pairId):
		""" get trade stat """
		query = """
			SELECT 
				SUM(cou) as cou,
				SUM(price_2_sum) as price_2_sum,
				SUM(price_sum) as price_sum
			FROM 
				s_trade_stats
			WHERE
				pair_id = {2} AND start_ts >= {0} AND start_ts < {1}
		""".format(startTS, endTS, pairId)
		
		cursor = self.connect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()
	
	def getSigma(self, TS, timeLen, pairId):
		""" get sigma timeLen setted in days """
		startTS = TS - int(timeLen) * self.SEC_ID_DAY

		rows = self.getPriceStat(startTS, TS, pairId)

		if len(rows) > 0:
			return (rows[0][1] / float(rows[0][0]) - rows[0][2] * rows[0][2] / float(rows[0][0]) / float(rows[0][0])) ** 0.5

		return 0

	def __del__(self):
		self.connect.close()
