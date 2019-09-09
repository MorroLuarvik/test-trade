#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот, их тут много будет """

from cascade import Cascade

class Bot:

	fee = 0.2
	minPrice = 1e-8
	maxPrice = 1
	minAmount = 0.05
	precision = 8

	exchange = None
	pairId = None
	curTS = None

	def __init__(self, exchange = None, pairId = 0, botType = "cascade"):
		self.exchange = exchange
		self.pairId = pairId

	def reset(self):
		""" сброс настроек """ 
		self.curTS = None

	def setTS(self, ts = None):
		""" установка времени сервера """
		if not self.curTS is None:
			self._action()
		self.curTS = ts

	def _action(self):
		""" торговые действия бота """
