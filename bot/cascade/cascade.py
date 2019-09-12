#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот, их тут много будет """

class Cascade:

	DECIMAL_PLACES = 8

	"""
	fee = 0.2
	minPrice = 1e-8
	maxPrice = 1
	minAmount = 0.05
	precision = 8
	"""

	exchange = None
	pairId = None
	curTS = None

	#параметры бота
	invest = None
	sigmaDays = None # кол-во дней, за которое высчитывается сигма
	sigmaLength = None # кол-во сигм
	sigmaIndent = None # стартовый отступ
	profitPercent = None
	incInvest = None
	selfInvest = None
	maxStages = 150

	#текущие хар-ки бота
	botId = None #id бота на бирже
	cascadeStruct = None
	curSigma = None
	curLastPrice = None
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
		self.curLastPrice = self.exchange.getLastPrice()

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
		minInvest = self.exchange.getMinAmount() / (100 - self.exchange.getFee()) * 100 * (2.0 + self.incInvest) / 2.0
		investDiv = minInvest * self.curLastPrice

		startPrice = self.curLastPrice - self.sigmaIndent * self.curSigma
		endPrice = self.curLastPrice - self.sigmaLength * self.curSigma

		steps = min(int(self.invest / investDiv), self.maxStages)

		investQuant = self.invest / float(steps)

		investOrders = self.___getInvestOrders(startPrice, endPrice, steps, investQuant, self.incInvest)
		return {
			'investOrders': investOrders,
			'profitOrders': self.___getProfitOrders(investOrders, [])
		}

	def ___getInvestOrders(self, startPrice, endPrice, steps, midInvest, incInvest = 0.0):
		""" создание инвестиционных ордеров """
		deltaPrice = (startPrice - endPrice) / float(steps)
		startInvest = midInvest / (1 + incInvest / 2.0)
		
		investOrders = []
		for stage in range(0, steps):
			price = startPrice - deltaPrice * stage
			invset = startInvest * (1 + incInvest * stage / (steps - 1)) 
			investOrders.append({
				'type': "buy",
				'amount': round(invset / price, self.exchange.getPrecision()),
				'price': round(price, self.DECIMAL_PLACES),
				'invest': invset
			})

		return investOrders

	def ___getProfitOrders(self, investOrders = None, profitOrders = []):
		""" создание профитных ордеров """
		profitAction = 'buy'
	
		invested = 0
		accepted = 0
		idx = 0
		for order in investOrders:
			accepted += order['amount'] * (100 - self.exchange.getFee()) / 100
			invested += order['amount'] * order['price']
			amount = accepted
			price = invested / accepted * (100 + self.profitPercent) / 100
			
			idx += 1
			if idx > len(profitOrders):
				profitOrders.append({
					'type': profitAction,
					'amount': round(amount, self.exchange.getPrecision()),
					'price': round(price, self.DECIMAL_PLACES)
				})
		return profitOrders

	def __checkOrderStatus(self, cascadeStruct):
		""" проверка состояния ордеров на бирже """
		orderIds = self.exchange.getActiveOrderIds(self.botId)
		for order in cascadeStruct['investOrders']:
			if self.___isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		for order in cascadeStruct['profitOrders']:
			if self.___isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		return cascadeStruct, False

	def ___isActiveOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 0:
			return True
		return False
	
	def ___isCreatedOrder(self, order):
		if 'orderId' in order:
			return True
		return False
	
	def ___isCompleteOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 1:
			return True
		return False

	def __inWork(self, cascadeStruct):
		""" проверка состояния ордеров находимся ли мы в сделке """
		for order in cascadeStruct['investOrders']:
			if self.___isCompleteOrder(order):
				return True
		
		return False

	def __needRestart(self, cascadeStruct):
		""" проверка необходимости перезапуска каскада """
		if self.curLastPrice > cascadeStruct['investOrders'][0]['price'] + self.curSigma * self.sigmaIndent:
			return True

		return False

	def __cancelOrders(self, cascadeStruct):
		""" отмена ордеров каскада каскада """
		for order in cascadeStruct['investOrders']:
			if self.___isActiveOrder(order):
				res, error = self.exchange.cancelOrder(self.botId, order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		for order in cascadeStruct['profitOrders']:
			if self.___isActiveOrder(order):
				res, error = self.exchange.cancelOrder(self.botId, order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		return cascadeStruct, False

	def __hasProfit(self, cascadeStruct): #sell order complete
		""" исполнен ли ордер на продажу """
		for order in cascadeStruct['profitOrders']:
			if self.___isCompleteOrder(order):
				return True
		
		return False

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
