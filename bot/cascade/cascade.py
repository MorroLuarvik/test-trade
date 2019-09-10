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

	#параметры бота
	invest = None
	sigmaDays = None
	sigmaLength = None
	sigmaIndent = None
	profitPercent = None
	incInvest = None
	selfInvest = None

	#текущие хар-ки бота
	botId = None #id бота на бирже

	def __init__(self, exchange = None, pairId = 0):
		self.exchange = exchange
		self.pairId = pairId

	def reset(self):
		""" сброс настроек """ 
		self.curTS = None

	def setParams(self, invest = None, sigmaDays = None, sigmaLength = None, sigmaIndent = None, profitPercent = None, incInvest = None, selfInvest = None):
		""" установка параметров бота """
		self.invest = invest
		self.sigmaDays = sigmaDays
		self.sigmaLength = sigmaLength
		self.sigmaIndent = sigmaIndent
		self.profitPercent = profitPercent
		self.incInvest = incInvest
		self.selfInvest = selfInvest

	def register(self):
		""" регистрация бота на бирже """
		if not self.botId is None:
			return False

		self.botId = self.exchange.register()
		return self.botId

	def addFunds(self):
		""" Внесение средств бота на баланс """
		if not self.botId is None:
			return False

		res, message = self.exchange.addFunds(self.botId, self.invest)
		if not res:
			print(message)
			exit()
		return res

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
				"default": 0.02,
				"mutable": False
			},
			"sigmaDays": {
				"mutable": True,
				"min": 5,
				"max": 60,
				"type": "int"
			},
			"sigmaLength": {
				"mutable": True,
				"min": 0.5,
				"max": 4,
				"type": "float"
			},
			"sigmaIndent": {
				"mutable": True,
				"min": 0,
				"max": 2,
				"type": "float"
			},
			"profitPercent": {
				"mutable": True,
				"min": 0.01,
				"max": 10,
				"type": "float"
			},
			"incInvest": {
				"mutable": True,
				"min": 0,
				"max": 7,
				"type": "int"
			},
			"selfInvest": {
				"mutable": True,
				"min": 0,
				"max": 1,
				"type": "bool"
			}
		}
