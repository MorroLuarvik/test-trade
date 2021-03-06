#!/usr/bin/env python
#-*-coding:utf-8-*-

from mysql import connector as MySQLdb

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

	def getCurrencyByAlias(self, alias = None):
		""" получения данных инструментов по алиасу """
		if not type(alias) is str:
			return False
		
		query = """
			SELECT *
			FROM s_currencys
			WHERE alias = "{0}"
		""".format(alias)

		cursor = self.connect.cursor()

		cursor.execute(query)
		return cursor.fetchall()
		
	def getPairByPairId(self, pairId = None):
		""" get pair info by pair id """
		if not type(pairId) is int:
			return False
		
		query = """
			select
				p.pair_id,
				p.pair_name,
				p.main_cur_id,
				m.alias as main_cur_alias,
				p.sec_cur_id,
				s.alias  as sec_cur_alias,
				p.disabled,
				p.decimal_places,
				p.min_price,
				p.max_price,
				p.min_amount,
				p.min_total,
				p.fee,
				p.is_invest_buy_fee,
				p.is_invest_sell_fee
			from s_pairs as p
			inner join s_currencys as m on p.main_cur_id = m.cur_id
			inner join s_currencys as s on p.sec_cur_id = s.cur_id
			where p.pair_id = {0}""".format(pairId)

		cursor = self.connect.cursor()

		cursor.execute(query)
		return cursor.fetchall()


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

		cursor = self.connect.cursor()
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
		
		cursor = self.connect.cursor()
		cursor.execute(query) 
		return cursor.fetchall()

	def __del__(self):
		self.connect.close()
