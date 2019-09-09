#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот, их тут много будет """

class Cascade:

	fee = 0.2
	minPrice = 1e-8
	maxPrice = 1
	minAmount = 0.05
	precision = 8

	exchange = None
	pairId = None
	curTS = None

	def __init__(self, exchange = None, pairId = 0):
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

	def getParamsTempalte(self):
		return {
			"invest": {
				"default": 0.2,
				"mutable": False
			},
			"sigmaDays": {
				"mutable": True,
				"min": 5,
				"max": 60
			},
			"sigmaLength": {
				"mutable": True,
				"min": 0.5,
				"max": 4
			},
			"sigmaIndent": {
				"mutable": True,
				"min": 0,
				"max": 2
			},
			"profitPercent": {
				"mutable": True,
				"min": 0.01,
				"max": 10
			},
			"incInvest": {
				"mutable": True,
				"min": 0,
				"max": 7
			}
		}
