#!/usr/bin/env python
#-*-coding:utf-8-*-

import sqlite3

class LocalData:


	curConnect = None
	pairId = None
	pairTableName = "s_trade_stats"

	def __init__(self, dbFileName = None, pairId = 0):
		self.pairId = pairId
		self.curConnect = sqlite3.connect(dbFileName)

	def migrateToMemory(self):
		tempConnect = sqlite3.connect(':memory:') # create a memory database
		query = "".join(line for line in self.curConnect.iterdump())
		tempConnect.executescript(query)
		self.curConnect = tempConnect


	def addPairStatistic(self, data = None):
		if not self.hasPairStatTable():
			self.createPairStatTable()

		self.clearPairStatTable(self.pairId)

		query = """
			INSERT INTO {0}
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""".format(self.pairTableName)

		cursor = self.curConnect.cursor()
		for row in data:
			inserted = row[:4] + (float(row[4]), ) + row[5:]
			cursor.execute(query, inserted)
			self.curConnect.commit()

	def hasPairStatTable(self):
		return self.__hasTable(self.pairTableName)

	def createPairStatTable(self):
		query = """
			CREATE TABLE {0} (
				pair_id,
				start_ts,
				end_ts,
				cou,
				price_open,
				price_min,
				price_max,
				price_close,
				amount_sum,
				amount_2_sum,
				price_sum,
				price_2_sum,
				volume_sum,
				volume_2_sum
			)
		""".format(self.pairTableName)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query)
		cursor = self.curConnect.commit()
	
	def clearPairStatTable(self, pairId = None):
		query = """
			DELETE FROM {0}
			WHERE pair_id = {1}
		""".format(self.pairTableName, pairId)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query)
		cursor = self.curConnect.commit()

	def __hasTable(self, tableName = None):
		if not type(tableName) is str:
			return False

		query = """
			SELECT name 
			FROM sqlite_master 
			WHERE type='table' AND name='{0}'
		""".format(tableName)

		cursor = self.curConnect.cursor()
		cursor.execute(query) 
		rows = cursor.fetchall()

		if len(rows) <= 0:
			return False
		
		if rows[0][0] > 0:
			return True
		
		return False

	def getTrades(self, startTS, endTS, timeDelta, pairId):
		query = """
			SELECT 
				MIN(price_min) as min_price,
				MAX(price_max) as max_price,
				start_ts / {2} as time_mark,
				(start_ts / {2}) * {2} as ts,
				CAST(SUBSTR(MIN(start_ts || price_open), 12) AS DECIMAL(16, 5)) as open_price,
				CAST(SUBSTR(MAX(end_ts || price_close), 12) AS DECIMAL(16, 5)) as close_price,
				SUM(amount_sum) as volume
			FROM 
				s_trade_stats
			WHERE
				pair_id = {3} AND start_ts BETWEEN {0} AND {1}
			GROUP BY
				time_mark
			ORDER BY
				time_mark
		""".format(startTS, endTS, timeDelta, pairId)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()


	def __del__(self):
		self.curConnect.close()
