#!/usr/bin/env python
#-*-coding:utf-8-*-

from .abstractdatasource import AbstractDatasource
from mysql import connector
import misc

class MySQL(AbstractDatasource):
	""" Источник данных MySQL """

	connect = None

	def __init__(self, host = None, db = None, user = None, password = None, port = 3306):
		""" инициализация источника данных """
		self.connect = connector.connect(
			host = host,
			user = user,
			password = password,
			db = db,
			port = port,
			charset = 'utf8',
			use_unicode = True)

	# ----------------------------- реализация функций абстрактного класса ----------------------------- #
	def get_exchange(self, **where):
		""" получение списка бирж """
		query = """
			select
				exch_id,
				exch_name,
				alias,
				exchange_class,
				disabled,
				using_rest
			from s_exchanges
			where %s""" % self._construct_where_conditions(**where)

		cursor = self.connect.cursor(dictionary = True)

		cursor.execute(query)
		return cursor.fetchall()

	def get_pair(self, **where):
		""" получение списка торговых пар """
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
			where %s""" % self._construct_where_conditions(**where)

		#print(query)

		cursor = self.connect.cursor(dictionary = True)

		cursor.execute(query)
		return cursor.fetchall()

	def get_trades_start_ts_range(self, pair_id = None):
		""" получить диапазон дат для пары, на которой накоплена статистика """
		query = """
			SELECT 
				MIN(start_ts) as min_start_ts,
				MAX(start_ts) as max_start_ts
			FROM 
				s_trade_stats
			WHERE
				%s
		""" % self._construct_where_conditions(pair_id = pair_id)
		
		cursor = self.connect.cursor(dictionary = True)
		
		cursor.execute(query) 
		return cursor.fetchall()

	def _construct_where_conditions(self, **where):
		""" сборка where условия SQL запроса """
		if len(where) == 0:
			return " 1 = 1 "
		if len(where) == 1 and list(where.values())[0] == None:
			return " 0 = 0 "

		ret_array = []
		for key, val in where.items():
			if misc.isIterable(val):
				ret_array.append("%s in (%s)" % (str(key),  ", ".join(map(str, val))))
				continue
			
			if val is None:
				ret_array.append("%s is null" % str(key))
				continue
			
			ret_array.append("%s = %s" % (str(key) , str(val)))
		
		return " and ".join(ret_array)
	# ----------------------------- реализация функций абстрактного класса ----------------------------- #

	def __del__(self):
		if self.connect.is_connected():
			self.connect.close()
