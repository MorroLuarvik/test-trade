#!/usr/bin/env python
#-*-coding:utf-8-*-

class AbstractDatasource:
	""" Абстрактный источник данных """

	def get_exchange(self, exch_ids = None):
		""" получить список бирж """
		raise NotImplementedError("Определите get_exchange в %s." % (self.__class__.__name__))

	def get_pair(self, pair_ids = None):
		""" получить список торговых пар """
		raise NotImplementedError("Определите get_pair в %s." % (self.__class__.__name__))
