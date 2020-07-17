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
	def get_exchange(self, exch_ids = None):
		""" получение списка бирж """
		where_conditions = {"where": "1 = 1"}
		
		if exch_ids is not None:
			where_conditions = {"where": "exch_id = %s" % str(exch_ids)}

			if misc.isIterable(exch_ids):
				where_conditions = {"where": "exch_id in (%s)" % ", ".join(map(str, exch_ids))}

		query = """
			select
				exch_id,
				exch_name,
				alias,
				exchange_class,
				disabled,
				using_rest
			from s_exchanges
			where %(where)s"""

		cursor = self.connect.cursor(dictionary = True)

		cursor.execute(query % where_conditions)
		return cursor.fetchall()

	def get_pair(self, pair_id = None):
		""" получение списка торговых пар """
		where_conditions = {"where": "1 = 1"}
		if pair_id is not None:
			where_conditions = {"where": "pair_id = %s" % int(pair_id)}

		query = """
			select
				exch_id,
				exch_name,
				alias,
				exchange_class,
				disabled,
				using_rest
			from s_exchanges
			where %(where)s"""

		cursor = self.connect.cursor(dictionary = True)

		cursor.execute(query % where_conditions)
		return cursor.fetchall()
	# ----------------------------- реализация функций абстрактного класса ----------------------------- #

	def __del__(self):
		self.connect.close()
