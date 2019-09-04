#!/usr/bin/env python
#-*-coding:utf-8-*-

import sqlite3

class LocalData:
	connect = None
	pairId = None
	pairTableName = "s_trade_stats"

	def __init__(self, dbFileName = None, pairId = 0):
		self.pairId = pairId
		self.connect = sqlite3.connect(dbFileName)

	def addPairStatistic(self, data = None):
		if not self.hasPairStatTable():
			self.createPairStatTable()

		self.clearPairStatTable(self.pairId)

		query = """
			INSERT INTO {0}
			VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""".format(self.pairTableName)

		cursor = self.connect.cursor()
		for row in data:
			inserted = row[:4] + (float(row[4]), ) + row[5:]
			cursor.execute(query, inserted)
			self.connect.commit()

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
		
		cursor = self.connect.cursor()
		cursor.execute(query)
		cursor = self.connect.commit()
	
	def clearPairStatTable(self, pairId = None):
		query = """
			DELETE FROM {0}
			WHERE pair_id = {1}
		""".format(self.pairTableName, pairId)
		
		cursor = self.connect.cursor()
		cursor.execute(query)
		cursor = self.connect.commit()

	def __hasTable(self, tableName = None):
		if not type(tableName) is str:
			return False

		query = """
			SELECT name 
			FROM sqlite_master 
			WHERE type='table' AND name='{0}'
		""".format(tableName)

		cursor = self.connect.cursor()
		cursor.execute(query) 
		rows = cursor.fetchall()

		if len(rows) <= 0:
			return False
		
		if rows[0][0] > 0:
			return True
		
		return False


	def __del__(self):
		self.connect.close()
