#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Симулятор биржы """

from collections.abc import Iterable
from misc import ceil

class Exchange:

	SEC_ID_DAY = 24 * 3600

	#fee = 0.2
	#minPrice = 1e-8 #1e-8 1
	#maxPrice = 1 #1e8 2e6
	#minAmount = 0.0001 # 0.05 -- 0.01 0.0001
	#precision = 8

	dataSource = None
	#pairId = None
	curTS = None

	nextUserId = 0
	nextOrderId = 0
	users = {}
	orders = {}
	reserves = {}

	def __init__(self, dataSource = None): #, pairId = 0
		self.dataSource = dataSource
		#self.pairId = pairId

	def reset(self):
		""" сброс настроек """ 
		Exchange.nextUserId = 0
		Exchange.nextOrderId = 0
		self.curTS = None
		self.users = {}
		self.orders = {}
		self.reserves = {}

	def setTS(self, ts = None):
		""" установка времени сервера """
		if not self.curTS is None:
			self._executeOrders(self.curTS, ts)
		self.curTS = ts

	def _executeOrders(self, startTS, endTS):
		""" выполнение ордеров """
		minPrice, maxPrice = self._getMinMaxPrice(startTS, endTS)

		if minPrice is False or minPrice is None:
			return

		for orderId in dict(filter(lambda item: item[1]['type'] == "buy" and item[1]['rate'] > minPrice, self.orders.items())):
			self._executeOrder(orderId)
		
		for orderId in dict(filter(lambda item: item[1]['type'] == "sell" and item[1]['rate'] < maxPrice, self.orders.items())):
			self._executeOrder(orderId)

	def _executeOrder(self, orderId):
		""" исполнение указанного ордера """
		if not orderId in self.orders:
			return False

		pairId = self.orders[orderId]["pair_id"]
		mainCurAlias = self.getMainCurAliasByPairId(pairId)
		secCurAlias = self.getSecCurAliasByPairId(pairId)
		precision = self.getOrderPrecisionByPairId(pairId)

		if self.orders[orderId]["type"] == "buy":

			if not mainCurAlias in self.users[self.orders[orderId]["user_id"]]["balance"]:
				self.users[self.orders[orderId]["user_id"]]["balance"][mainCurAlias] = 0

			if self.isInvestFeeByPairId(pairId):
				self.users[self.orders[orderId]["user_id"]]["balance"][mainCurAlias] +=	self.orders[orderId]["amount"]
				del self.reserves[orderId]
			else:
				self.users[self.orders[orderId]["user_id"]]["balance"][mainCurAlias] += ceil(self.orders[orderId]["amount"] * (100 - self.getOrderFeeByPairId(pairId)) / 100, precision)
		else:
			if not secCurAlias in self.users[self.orders[orderId]["user_id"]]["balance"]:
				self.users[self.orders[orderId]["user_id"]]["balance"][secCurAlias] = 0

			self.users[self.orders[orderId]["user_id"]]["balance"][secCurAlias] += ceil(self.orders[orderId]["amount"] * self.orders[orderId]["rate"] * (100 - self.getOrderFeeByPairId(pairId)) / 100, precision)
		del self.orders[orderId]

		return True

	def _getMinMaxPrice(self, startTS, endTS):
		""" получение минимальной и максимальной цен за период """
		rows = self.dataSource.getMinMaxTrades(startTS, endTS, self.pairId)
		if len(rows) == 0:
			return False, False

		return rows[0][0], rows[0][1]

	def register(self):
		""" регистрация пользователя """
		userId = Exchange.nextUserId
		Exchange.nextUserId += 1
		self.users[userId] = {}
		return userId

	def addFunds(self, userId = 0, curAlias = None, funds = 0):
		""" внесение средств на баланс"""
		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"
		
		if not type(curAlias) is str:
			return False, "unknown currency: " + str(curAlias)

		curAlias = curAlias.lower()

		if not self._hasCurrency(curAlias):
			return False, "unknown currency: " + str(curAlias)

		if not "balance" in self.users[userId]:
			self.users[userId]["balance"] = {}

		if not curAlias in self.users[userId]["balance"]:
			self.users[userId]["balance"][curAlias] = 0

		self.users[userId]["balance"][curAlias] += funds
		return True, "funds for user with id: " + str(userId) + " added successfull. Your " + str(curAlias) + "balance " + str(self.users[userId]["balance"][curAlias])


	def _hasCurrency(self, curAlias = None):
		""" проверка существования валюты """
		rows = self.dataSource.getCurrencyByAlias(curAlias)
		if not rows:
			return False

		if len(rows) == 0:
			return False
		
		return True

	def createOrder(self, userId = 0, pairId = None, orderType = "buy", amount = 0, rate = 0):
		""" cоздание ордера """
		if self.curTS is None:
			return False, "exchange TS is not setted"

		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"

		if rate <= self.getMinOrderPrice(pairId) or rate >= self.getMaxOrderPrice(pairId):
			return False, "rate must be in " + str(self.getMinOrderPrice(pairId)) + " - " + str(self.getMaxOrderPrice(pairId)) + " interval"
		
		if amount < self.getMinOrderAmount(pairId):
			return False, "amount must be large than " + str(self.getMinOrderAmount(pairId))

		if not "balance" in self.users[userId]:
			return False, "not has balance to create order"

		mainCurAlias = self.getMainCurAliasByPairId(pairId)
		secCurAlias = self.getSecCurAliasByPairId(pairId)

		if orderType == "buy":
			if not secCurAlias in self.users[userId]["balance"]:
				return False, "not has " + secCurAlias + " funds in balance to create order"
			if self.isInvestFeeByPairId(pairId):
				if self.users[userId]["balance"][secCurAlias] < rate * amount * (100 + self.getOrderFeeByPairId(pairId)) / 100:
					return False, "not enough funds in sec balance " + str(self.users[userId]["balance"][secCurAlias]) + " less  than " + str(rate * amount * (100 + self.getOrderFeeByPairId(pairId)) / 100)
			else:
				if self.users[userId]["balance"][secCurAlias] < rate * amount:
					return False, "not enough funds in sec balance " + str(self.users[userId]["balance"][secCurAlias]) + " less  than " + str(rate * amount)
		else:
			if not mainCurAlias in self.users[userId]["balance"]:
				return False, "not has main funds in balance to create order"
			if self.users[userId]["balance"][mainCurAlias] < amount:
				return False, "not enough funds in main balance " + str(self.users[userId]["balance"][mainCurAlias]) + " less than " + str(amount) + " look delta " + str(self.users[userId]["balance"][mainCurAlias] - amount)

		#change balance
		if orderType == "buy":
			self.users[userId]["balance"][secCurAlias] -= ceil(rate * amount, self.getOrderPrecisionByPairId(pairId))
		else:
			self.users[userId]["balance"][mainCurAlias] -= amount

		#create order
		orderId = Exchange.nextOrderId
		Exchange.nextOrderId += 1
		self.orders[orderId] = {
			"user_id": userId,
			"pair_id": pairId,
			"create_ts": self.curTS,
			"type": orderType,
			"rate": rate,
			"amount": amount
		}
		
		#create fee reserve
		if self.isInvestFeeByPairId(pairId) and orderType == "buy":
			self.users[userId]["balance"][secCurAlias] -= ceil(rate * amount * self.getOrderFeeByPairId(pairId) / 100, self.getOrderPrecisionByPairId(pairId))
			self.reserves[orderId] = ceil(rate * amount * self.getOrderFeeByPairId(pairId) / 100, self.getOrderPrecisionByPairId(pairId))
			self.getOrderFeeByPairId(pairId)
		
		return orderId, "order created"

	def cancelOrder(self, userId = 0, orderId = 0):
		""" отмена ордера """
		
		if not orderId in self.orders:
			return False, "Can't cancel order " + str(orderId) + ". Order not found."

		if self.orders[orderId]['user_id'] != userId:
			return False, "Can't cancel order " + str(orderId) + ". It is not your order."
		
		mainCurAlias = self.getMainCurAliasByPairId(self.orders[orderId]["pair_id"])
		secCurAlias = self.getSecCurAliasByPairId(self.orders[orderId]["pair_id"])

		if self.orders[orderId]["type"] == "buy":
			self.users[userId]["balance"][secCurAlias] += self.orders[orderId]["rate"] * self.orders[orderId]["amount"]
			if self.isInvestFeeByPairId(self.orders[orderId]["pair_id"]):
				self.users[userId]["balance"][secCurAlias] += self.reserves[orderId]
				del self.reserves[orderId]
		else:
			self.users[userId]["balance"][mainCurAlias] += self.orders[orderId]["amount"]

		del self.orders[orderId]
		
		#print("cancel order {0}".format(orderId))
		
		return True, "order canceled"

	def getActiveOrderIds(self, userId = 0):
		""" получение списка id активных ордеров """
		return dict(filter(lambda item: item[1]['user_id'] == userId, self.orders.items())).keys()

	def getLastPrice(self):
		""" получение последней цены согласно таймеру """
		rows = self.dataSource.getLastPrice(self.curTS, self.pairId)
		if len(rows) <= 0:
			return False
		
		return rows[0][0]
	
	def getSigma(self, timeLen):
		""" get sigma """
		return self.dataSource.getSigma(self.curTS, timeLen, self.pairId)

	def getTotalBalance(self, userId = 0):
		""" получение последней цены согласно таймеру """
		lastPrice = self.getLastPrice()
		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"

		return self.users[userId]["balance"]["sec"] + self.users[userId]["balance"]["main"] * lastPrice + sum(val["amount"] * val["rate"] for val in self.orders.values() if val["user_id"] == userId and val["type"] == "buy") + sum(val["amount"] * lastPrice for val in self.orders.values() if val["user_id"] == userId and val["type"] == "sell")

	# ================================== get trade params ================================== #
	def getMinOrderPrice(self, pairId = None):
		""" возвращает минимальную цену ордера для торговой пары """
		if not type(pairId) is int:
			return False

		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[8]
		
		return False

	def getMaxOrderPrice(self, pairId = None):
		""" возвращает максимальную цену ордера для торговой пары """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[9]
		
		return False

	def getMinOrderAmount(self, pairId = None):
		""" get min amount in order """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[10]
		
		return False

	def getOrderFeeByPairId(self, pairId = None):
		""" get fee in order """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[12]
		
		return False

	def getOrderPrecisionByPairId(self, pairId = None):
		""" get precision in order """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[7]
		
		return False

	def getMainCurAliasByPairId(self, pairId = None):
		""" get main cur alias for pair ID """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[3]
		
		return False

	def getSecCurAliasByPairId(self, pairId = None):
		""" get sec cur alias for pair ID """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[5]
		
		return False

	def isInvestFeeByPairId(self, pairId = None):
		""" get flag when fee get from invest for pair ID """
		if not type(pairId) is int:
			return False
		
		params = self._getPairParams(pairId)
		if isinstance(params, Iterable):
			return params[13]
		
		return False

	def _getPairParams(self, pairId = None):
		""" получает ограничения на создиние ордеров для торговой пары 
			0	p.pair_id,
			1	p.pair_name,
			2	p.main_cur_id,
			3	m.alias as main_cur_alias,
			4	p.sec_cur_id,
			5	s.alias  as sec_cur_alias,
			6	p.disabled,
			7	p.decimal_places,
			8	p.min_price,
			9	p.max_price,
			10	p.min_amount,
			11	p.min_total,
			12	p.fee,
			13	p.is_invest_buy_fee,
			14	p.is_invest_sell_fee
		"""
		if not type(pairId) is int:
			return False

		rows = self.dataSource.getPairByPairId(int(pairId))
		if not rows:
			return False

		if len(rows) == 0:
			return False

		return rows[0]

	#def ceil(self, i, n=0):
	#	""" округление с отбрасыванием дробного """ 
	#	return int(i * 10 ** n) / float(10 ** n)
