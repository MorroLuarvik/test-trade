#!/usr/bin/env python
#-*-coding:utf-8-*-

class AbstractDatasource:
	""" Абстрактный источник данных """

	def get_exchange(self, exch_id = None):
		""" получить список бирж """
		raise NotImplementedError("Определите get_exchange в %s." % (self.__class__.__name__))

	def get_pair(self, exch_id = None, pair_id = None):
		""" получить список торговых пар """
		raise NotImplementedError("Определите get_pair в %s." % (self.__class__.__name__))
	
	def get_trades_start_ts_range(self, pair_id = None):
		""" получить диапазон дат для пары, на которой накоплена статистика """
		raise NotImplementedError("Определите get_trades_start_ts_range в %s." % (self.__class__.__name__))
