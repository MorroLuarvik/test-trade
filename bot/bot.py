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

	curBot = None

	def __init__(self, exchange = None, pairId = 0, botType = "cascade"):
		self.exchange = exchange
		self.pairId = pairId

		#create bot dependet by botType var
		self.curBot = Cascade(self.exchange, self.pairId)

	def init(self, params = None):
		""" иницализация бота """
		if params is None:
			self.curBot.setParams(**self._mutateParams(self.curBot.getParamsTempalte())) #TODO нужно предусмотреть результаты реального тестирования
		else: # костыль для проверки множественности ботов
			ownParams = self._mutateParams(self.curBot.getParamsTempalte())
			ownParams["sigmaIndent"] = params
			self.curBot.setParams(**ownParams)

		self.curBot.register()
		self.curBot.addFunds()

	def _mutateParams(self, paramsTemplate = None):
		""" генерация параметров бота, пока используется залипуха для тестирования """
		return {
			"invest": 0.04,
			"sigmaDays": 23,
			"sigmaLength": 3.2,
			"sigmaIndent": 0.15,
			"profitPercent": 1.1,
			"incInvest": 5,
			"selfInvest": True
		}

	def reset(self):
		""" сброс настроек """ 
		self.curTS = None
		self.curBot.reset()

	def setTS(self, ts = None):
		""" установка времени сервера """
		if not self.curTS is None:
			self.curBot.setTS(ts) #за одно и бота запускаем
		self.curTS = ts