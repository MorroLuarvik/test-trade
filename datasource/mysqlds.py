#!/usr/bin/env python
#-*-coding:utf-8-*-

from .abstractdatasource import AbstractDatasource
from mysql import connector

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
	def get_exchange(self, exch_id = None):
		""" получение списка бирж """
		where_conditions = {"where": "1 = 1"}
		if exch_id is not None:
			where_conditions = {"where": "exch_id = %s" % exch_id}

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
