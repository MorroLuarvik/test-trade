#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот, их тут много будет """

from abstractbot import AbstractBot

class Cascade(AbstractBot):

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
	activeOrdersCount = 2
	
	autoRepeat = True

	#текущие хар-ки бота
	botId = None #id бота на бирже
	cascadeStruct = None
	curSigma = None
	curLastPrice = None
	status = None
	changeStatusTS = None

	def __init__(self, exchange = None, pairId = 0):
		AbstractBot.__init__(self, exchange, pairId)
		self.exchange = exchange
		self.pairId = pairId

	def reset(self):
		""" сброс настроек """ 
		self.curTS = None

		self.autoRepeat = True
	
		self.botId = None #id бота на бирже
		self.cascadeStruct = None
		self.curSigma = None
		self.curLastPrice = None
		self.status = None
		self.changeStatusTS = None

	def setParams(self, invest = None, sigmaDays = None, sigmaLength = None, sigmaIndent = None, profitPercent = None, incInvest = None, selfInvest = None):
		""" установка параметров бота """
		self.invest = invest
		self.sigmaDays = sigmaDays
		self.sigmaLength = sigmaLength
		self.sigmaIndent = sigmaIndent
		self.profitPercent = profitPercent
		self.incInvest = incInvest
		self.selfInvest = selfInvest

	def getParams(self):
		""" возвращает словарь с парамтерами бота """
		return {
			'invest': self.invest,
		'sigmaDays': self.sigmaDays,
		'sigmaLength': self.sigmaLength,
		'sigmaIndent': self.sigmaIndent,
		'profitPercent': self.profitPercent,
		'incInvest': self.incInvest,
		'selfInvest': self.selfInvest
		}

	def register(self):
		""" регистрация бота на бирже """
		if not self.botId is None:
			return False

		self.botId = self.exchange.register()
		return self.botId

	def addFunds(self):
		""" Внесение средств бота на баланс """
		if self.botId is None:
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

	def getBalance(self):
		""" возвращает полный баланс на exchange """
		return self.exchange.getTotalBalance(self.botId)

	def getCascadeStatus(self):
		if self.cascadeStruct is None:
			return "0/0"

		idx = 0
		for order in self.cascadeStruct['investOrders']:
			if self.isActiveOrder(order):
				break
			idx += 1

		return str(idx) + "/" + str(len(self.cascadeStruct['investOrders']))

	def stop(self):
		""" отмена всех ордеров и остановка каскада """
		self.cascadeStruct, error = self.__cancelOrders(self.cascadeStruct)
		if error:
			print('bot {1} error with cancelOrders in stop action: {0}'.format(error, self.botId)) #reportCancelOrdersError()
			quit()
		self.cascadeStruct = None
		self.status = 'stopped'

	def _action(self):
		""" торговые действия бота """
		if self.status == 'stopped':
			return

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
		else:
			if not self.autoRepeat:
				self.cascadeStruct, error = self.__cancelOrders(self.cascadeStruct)
				if error:
					print('bot {1} error with cancelOrders in cascade get profit: {0}'.format(error, self.botId)) #reportCancelOrdersError()
					quit()
				self.cascadeStruct = None
				self.status = 'stopped'
				return
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
				if self.autoRepeat:
					self.status = 'waiting'
				else:
					self.status = 'stopped'
			return
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
				'amount': self.ceil(invset / price, self.exchange.getPrecision()),
				'price': self.ceil(price, self.DECIMAL_PLACES),
				'invest': invset
			})

		return investOrders

	def ___getProfitOrders(self, investOrders = None, profitOrders = []):
		""" создание профитных ордеров """
		profitAction = 'sell'
	
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
					'amount': self.ceil(amount, self.exchange.getPrecision()),
					'price': self.ceil(price, self.DECIMAL_PLACES)
				})
		return profitOrders

	def __checkOrderStatus(self, cascadeStruct):
		""" проверка состояния ордеров на бирже """
		orderIds = self.exchange.getActiveOrderIds(self.botId)
		for order in cascadeStruct['investOrders']:
			if self.isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		for order in cascadeStruct['profitOrders']:
			if self.isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		return cascadeStruct, False

	def __inWork(self, cascadeStruct):
		""" проверка состояния ордеров находимся ли мы в сделке """
		for order in cascadeStruct['investOrders']:
			if self.isCompleteOrder(order):
				return True
		
		return False

	def __needRestart(self, cascadeStruct):
		""" проверка необходимости перезапуска каскада """
		if self.curLastPrice > cascadeStruct['investOrders'][0]['price'] + self.curSigma * self.sigmaIndent:
			print("bot #{0} restart cascase at {1}".format(self.botId, self.TStoStr(self.curTS)))
			return True

		return False

	def __cancelOrders(self, cascadeStruct):
		""" отмена ордеров каскада каскада """
		for order in cascadeStruct['investOrders']:
			if self.isActiveOrder(order):
				res, error = self.exchange.cancelOrder(self.botId, order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		for order in cascadeStruct['profitOrders']:
			if self.isActiveOrder(order):
				res, error = self.exchange.cancelOrder(self.botId, order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		return cascadeStruct, False

	def __hasProfit(self, cascadeStruct): #sell order complete
		""" исполнен ли ордер на продажу """
		for order in cascadeStruct['profitOrders']:
			if self.isCompleteOrder(order):
				return True
		
		return False

	def __reportProfit(self, cascadeStruct): #sell order complete
		""" сообщаем о получении профита и увеличиваем инвестиции, если необходимо"""
		investRatio = 1
		profitRatio = (100 - self.exchange.getFee()) / 100
		
		cou = 0
		invested = 0
		for profitOrder in cascadeStruct['profitOrders']:
			invested += cascadeStruct['investOrders'][cou]['price'] * cascadeStruct['investOrders'][cou]['amount'] * investRatio
			if self.isCompleteOrder(profitOrder):
				profitVal = self.ceil(profitOrder['amount'] * profitOrder['price'] * profitRatio - invested, self.exchange.getPrecision())
				print("bot {0} has profit {1}".format(self.botId, profitVal))
				if self.selfInvest:
					self.invest += profitVal
				break
			cou += 1

	def __hasPartialExecution(self, cascadeStruct):
		""" проверка частичного исполнения каскада """
		cou = 0
		for profitOrder in cascadeStruct['profitOrders']:
			if self.isCompleteOrder(profitOrder):
				break
			cou += 1
		
		if cou == len(cascadeStruct['profitOrders']) - 1:
			return False
		
		for investOrder in cascadeStruct['investOrders'][cou + 1:]:
			if self.isCompleteOrder(investOrder):
				return True
		
		return False

	def __resizeAfterProfit(self, cascadeStruct):
		""" изменение каскада после частичного исполнения """
		cou = 0
		for profitOrder in cascadeStruct['profitOrders']:
			if self.isCompleteOrder(profitOrder):
				break
			cou += 1
		
		cascadeStruct['investOrders'] = cascadeStruct['investOrders'][cou + 1:]
		cascadeStruct['profitOrders'] = self.___getProfitOrders(cascadeStruct['investOrders'], [])
		
		return cascadeStruct

	def __shiftOrders(self, cascadeStruct):
		""" сдвиг ордеров согласно изменённым ценам """
		idx = -1
		for order in cascadeStruct['investOrders']:
			if not self.isCreatedOrder(order):
				break
			idx += 1
		
		idx = max(idx, 0)
		
		if idx >= len(cascadeStruct['investOrders']) - 1: # all invest is created nothing to shift
			return cascadeStruct
	
		endPriceDirect = -1
	
		startPrice = cascadeStruct['investOrders'][idx]['price']
		endPrice = self.curLastPrice + self.sigmaLength * self.curSigma * endPriceDirect
		
		if endPrice > startPrice:
			return cascadeStruct

		steps = len(cascadeStruct['investOrders']) - idx
		
		cascadeStruct['investOrders'] = cascadeStruct['investOrders'][:idx + 1] + self.___resizeInvestOrders(cascadeStruct['investOrders'][idx:], startPrice, endPrice, steps)[1:]
		
		cascadeStruct['profitOrders'] = self.___getProfitOrders(cascadeStruct['investOrders'], cascadeStruct['profitOrders'][:idx + 1])
	
		return cascadeStruct

	def ___resizeInvestOrders(self, orders, startPrice, endPrice, steps):
		cou = 0
		for order in orders:
			order['price'] = self.ceil(startPrice + (endPrice - startPrice) * cou / float(steps-1), self.exchange.getPrecision())
			invest = order['invest']
			
			amount = self.ceil(invest / order['price'], self.DECIMAL_PLACES)
			
			order['amount'] = amount
			cou += 1
		return orders


	def __createOrders(self, cascadeStruct):
		""" создание инвестиционных ордеров """
		ordersCount = 0
		lastIdx = 0
		for order in cascadeStruct['investOrders']:
			if self.isActiveOrder(order):
				ordersCount += 1
			if not self.isCreatedOrder(order):
				break
			lastIdx += 1
		
		if lastIdx >= len(cascadeStruct['investOrders']): # all invest orders complete
			return cascadeStruct, False

		for idx in range(lastIdx, lastIdx + self.activeOrdersCount - ordersCount):
			if idx < len(cascadeStruct['investOrders']):
				orderId, error = self.createOrder(cascadeStruct['investOrders'][idx])
				if orderId is False:
					return cascadeStruct, error
				else:
					cascadeStruct['investOrders'][idx]['orderId'] = orderId
					"""
					if orderId is 0:
						cascadeStruct['investOrders'][idx]['status'] = 1
					else:
					"""
					cascadeStruct['investOrders'][idx]['status'] = 0
		
		return cascadeStruct, False

	def __moveProfitOrder(self, cascadeStruct):
		""" отмена неактуального профитного ордера и создание актуального """
		if not self.isCompleteOrder(cascadeStruct['investOrders'][0]): # no complete - no move
			return cascadeStruct, False
		
		completeIdx = -1
		for order in cascadeStruct['investOrders']:
			if not self.isCompleteOrder(order):
				break
			completeIdx += 1
		
		idx = 0
		for order in cascadeStruct['profitOrders']: # cancel prev profit order
			if self.isActiveOrder(order) and idx < completeIdx:
				res, error = self.exchange.cancelOrder(self.botId, order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
			idx += 1
	
		if self.isCreatedOrder(cascadeStruct['profitOrders'][completeIdx]): # profit order already exists
			return cascadeStruct, False
			
		orderId, error = self.createOrder(cascadeStruct['profitOrders'][completeIdx])
		if orderId is False:
			return cascadeStruct, error
		else:
			cascadeStruct['profitOrders'][completeIdx]['orderId'] = orderId
			if orderId is 0:
				cascadeStruct['profitOrders'][completeIdx]['status'] = 1
			else:
				cascadeStruct['profitOrders'][completeIdx]['status'] = 0
		
		return cascadeStruct, False

	def getChangeStatusTS(self):
		return self.changeStatusTS

	def getParamsTempalte(self):
		return {
			"invest": {
				"default": 0.03983,
				"mutable": False
			},
			"sigmaDays": {
				"default": 15,
				"mutable": True,
				"min": 5,
				"max": 60,
				"type": "int"
			},
			"sigmaLength": {
				"default": 3.2,
				"mutable": True,
				"min": 0.5,
				"max": 4,
				"type": "float"
			},
			"sigmaIndent": {
				"default": 0.15,
				"mutable": True,
				"min": 0,
				"max": 2,
				"type": "float"
			},
			"profitPercent": {
				"default": 1.1,
				"mutable": True,
				"min": 0.4,
				"max": 10,
				"type": "float"
			},
			"incInvest": {
				"default": 3,
				"mutable": True,
				"min": 0,
				"max": 7,
				"type": "int"
			},
			"selfInvest": {
				"default": True,
				"mutable": True,
				"min": 0,
				"max": 1,
				"type": "bool"
			}
		}
