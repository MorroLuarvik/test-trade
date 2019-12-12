#!/usr/bin/env python
#-*-coding:utf-8-*-

import sqlite3

class LocalData:


	curConnect = None
	pairId = None
	pairTableName = "s_trade_stats"

	SEC_ID_DAY = 24 * 3600

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
				pair_id INTEGER,
				start_ts INTEGER,
				end_ts INTEGER,
				cou INTEGER,
				price_open REAL,
				price_min REAL,
				price_max REAL,
				price_close REAL,
				amount_sum REAL,
				amount_2_sum REAL,
				price_sum REAL,
				price_2_sum REAL,
				volume_sum REAL,
				volume_2_sum REAL
			);
		""".format(self.pairTableName)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query)
		cursor = self.curConnect.commit()
	
		query = """
			CREATE INDEX pair_id_idx ON {0} (pair_id);
		""".format(self.pairTableName)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query)
		cursor = self.curConnect.commit()
		
		query = """
			CREATE INDEX start_ts_idx ON {0} (start_ts);
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
		""" get trade candles """
		query = """
			SELECT 
				MIN(price_min) as min_price,
				MAX(price_max) as max_price,
				start_ts / {2} as time_mark,
				(start_ts / {2}) * {2} as ts,
				CAST(SUBSTR(MIN(start_ts || price_open), 11) AS DECIMAL(16, 5)) as open_price,
				CAST(SUBSTR(MAX(end_ts || price_close), 11) AS DECIMAL(16, 5)) as close_price,
				SUM(amount_sum) as volume
			FROM 
				s_trade_stats
			WHERE
				pair_id = {3} AND start_ts > {0} AND start_ts <= {1}
			GROUP BY
				time_mark
			ORDER BY
				time_mark
		""".format(startTS, endTS, timeDelta, pairId)

		#		CAST(SUBSTR(MIN(start_ts || price_open), 12) AS DECIMAL(16, 5)) as open_price,
		#		CAST(SUBSTR(MAX(end_ts || price_close), 12) AS DECIMAL(16, 5)) as close_price,

		cursor = self.curConnect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()
	
	def getMinMaxTrades(self, startTS, endTS, pairId):
		""" get min and max trade values """
		query = """
			SELECT 
				MIN(price_min) as min_price,
				MAX(price_max) as max_price
			FROM 
				s_trade_stats
			WHERE
				pair_id = {2} AND start_ts >= {0} AND start_ts < {1}
		""".format(startTS, endTS, pairId)
		
		cursor = self.curConnect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()
	
	def getLastPrice(self, TS, pairId):
		""" получение цены закрытия согласно TS """
		query = """
			SELECT 
				price_close
			FROM 
				s_trade_stats
			WHERE
				pair_id = {1} AND start_ts < {0}
			ORDER BY start_ts DESC
			LIMIT 1
		""".format(TS, pairId)

		cursor = self.curConnect.cursor()
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
		
		cursor = self.curConnect.cursor()
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
		
		cursor = self.curConnect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()

	def getSigma(self, TS, timeLen, pairId):
		""" get sigma timeLen setted in days """
		startTS = TS - int(timeLen) * self.SEC_ID_DAY

		rows = self.getPriceStat(startTS, TS, pairId)

		if len(rows) > 0:
			return (rows[0][1] / rows[0][0] - rows[0][2] * rows[0][2] / rows[0][0] / rows[0][0]) ** 0.5

		return 0


	def __del__(self):
		self.curConnect.close()
