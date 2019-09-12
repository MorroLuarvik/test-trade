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
	sigmaDays = None # кол-во дней, за которое высчитывается сигма
	sigmaLength = None
	sigmaIndent = None
	profitPercent = None
	incInvest = None
	selfInvest = None

	#текущие хар-ки бота
	botId = None #id бота на бирже
	cascadeStruct = None
	curSigma = None
	status = None
	changeStatusTS = None

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
		oldTS = self.curTS 
		self.curTS = ts

		if not oldTS is None:
			self._action()


	def _action(self):
		""" торговые действия бота """
		self.curSigma = self.exchange.getSigma(self.sigmaDays)
		if self.cascadeStruct is None:
			self.cascadeStruct = self.__createCascade()
			self.status = 'waiting'
			self.changeStatusTS = self.curTS

		self.cascadeStruct, error = self.__checkOrderStatus(self.cascadeStruct)
		if error:
			print('bot {1} error with checkOrders in init: {0}'.format(error, self.botId))
			quit()
		
		# ================== check inWork status ================== #
		if self.__inWork(self.cascadeStruct):
			if self.status <> 'inWork':
				self.status = 'inWork'
				self.changeStatusTS = self.curTS

		# ================== check inWork status ================== #

		# ================== restart cascade ================== #
		if not self.__inWork(self.cascadeStruct) and self.__needRestart(self.cascadeStruct):
			self.cascadeStruct, error = self.__cancelOrders(self.cascadeStruct)
			if error:
				print('bot {1} error with cancelOrders in restart cascade: {0}'.format(error, self.botId)) #reportCancelOrdersError()
				quit()

			self.cascadeStruct = self.__createCascade()
			self.cascadeStruct, error = self.__checkOrderStatus(self.cascadeStruct)
			if error:
				print('bot {1} error with checkOrders in restart: {0}'.format(error, self.botId)) #reportCheckOrdersStatusError()
				quit()
		# ================== restart cascade ================== #
		
		# ================== cascade get profit ================== #
		if self.__hasProfit(self.cascadeStruct): #sell order complete
			self.__reportProfit(self.cascadeStruct)
			self.changeStatusTS = self.curTS
			if self.__hasPartialExecution(self.cascadeStruct): # need check executed next buy order
				print('bot {0} partial execution'.format(self.botId))
				self.cascadeStruct = self.__resizeAfterProfit(self.cascadeStruct)
			else:
				self.cascadeStruct, error = self.__cancelOrders(self.cascadeStruct)
				if error:
					print('bot {1} error with cancelOrders in cascade get profit: {0}'.format(error, self.botId)) #reportCancelOrdersError()
					quit()
				self.cascadeStruct = None
				self.status = 'waiting'
		# ================== cascade get profit ================== #

		# ================== create order sequence ================== #
		self.cascadeStruct = self.__shiftOrders(self.cascadeStruct)
		self.cascadeStruct, error = self.__createOrders(self.cascadeStruct)
		if error:
			print('bot {1} error with createOrders in create order sequence: {0}'.format(error, self.botId))

		self.cascadeStruct, error = self.__moveProfitOrder(self.cascadeStruct)
		if error:
			print('bot {1} error with moveProfitOrder in create order sequence: {0}'.format(error, self.botId)) #reportMoveProfitOrderError()
		# ================== create order sequence ================== #


	def __createCascade(self):
		""" создание каскада согласно параметрам текущего класса """
		pass # TODO realise

	def __checkOrderStatus(self, cascadeStruct):
		""" проверка состояния ордеров на бирже """
		pass # TODO realise

	def __inWork(self, cascadeStruct):
		""" проверка состояния ордеров находимся ли мы в сделке """
		pass # TODO realise

	def __needRestart(self, cascadeStruct):
		""" проверка необходимости перезапуска каскада """
		pass # TODO realise

	def __cancelOrders(self, cascadeStruct):
		""" отмена ордеров каскада каскада """
		pass # TODO realise

	def __hasProfit(self, cascadeStruct): #sell order complete
		""" исполнен ли ордер на продажу """
		pass # TODO realise

	def __reportProfit(self, cascadeStruct): #sell order complete
		""" отчёт о получении профита """
		pass # TODO realise

	def __hasPartialExecution(self, cascadeStruct):
		""" проверка частичного исполнения каскада """
		pass # TODO realise

	def __resizeAfterProfit(self, cascadeStruct):
		""" изменение каскада после частичного исполнения """
		pass # TODO realise

	def __shiftOrders(self, cascadeStruct):
		""" сдвиг ордеров согласно изменённым ценам """
		pass # TODO realise

	def __createOrders(self, cascadeStruct):
		""" создание инвестиционных ордеро """
		pass # TODO realise

	def __moveProfitOrder(self, cascadeStruct):
		""" отмена неактуального профитного ордера и создание актуального """
		pass # TODO realise

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
