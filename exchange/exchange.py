#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Симулятор биржы """

class Exchange:

	SEC_ID_DAY = 24 * 3600

	fee = 0.2
	minPrice = 1e-8
	maxPrice = 1e8
	minAmount = 0.01
	precision = 8

	dataSource = None
	pairId = None
	curTS = None

	nextUserId = 0
	nextOrderId = 0
	users = {}
	orders = {}

	def __init__(self, dataSource = None, pairId = 0):
		self.dataSource = dataSource
		self.pairId = pairId

	def reset(self):
		""" сброс настроек """ 
		Exchange.nextUserId = 0
		Exchange.nextOrderId = 0
		self.curTS = None
		self.users = {}
		self.orders = {}

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

		if self.orders[orderId]["type"] == "buy":
			self.users[self.orders[orderId]["user_id"]]["balance"]["main"] += round(self.orders[orderId]["amount"] * (100 - self.fee) / 100, self.precision)
		else:
			self.users[self.orders[orderId]["user_id"]]["balance"]["sec"] += round(self.orders[orderId]["amount"] * self.orders[orderId]["rate"] * (100 - self.fee) / 100, self.precision)
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

	def addFunds(self, userId = 0, funds = 0):
		""" внесение ОСНОВНЫХ средств  на баланс"""
		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"

		if not "balance" in self.users[userId]:
			self.users[userId]["balance"] = {}

		if not "main" in self.users[userId]["balance"]:
			self.users[userId]["balance"]["main"] = 0
			## ============== костыль ============== ##
			self.users[userId]["balance"]["main"] += self.minAmount / 100
			## ============== костыль ============== ##

		if not "sec" in self.users[userId]["balance"]:
			self.users[userId]["balance"]["sec"] = funds
			return True, "funds for user with id: " + str(userId) + " added successfull"

		self.users[userId]["balance"]["sec"] += funds
		return True, "funds for user with id: " + str(userId) + " added successfull"

	def createOrder(self, userId = 0, orderType = "buy", amount = 0, rate = 0):
		""" cоздание ордера """
		if self.curTS is None:
			return False, "exchange TS is not setted"

		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"

		if rate <= self.minPrice or rate >= self.maxPrice:
			return False, "rate must be in " + str(self.minPrice) + " - " + str(self.maxPrice) + " interval"
		
		if amount < self.minAmount:
			return False, "amount must be large than " + str(self.minAmount)

		if not "balance" in self.users[userId]:
			return False, "not has balance to create order"

		if orderType == "buy":
			if not "sec" in self.users[userId]["balance"]:
				return False, "not has sec funds in balance to create order"
			if self.users[userId]["balance"]["sec"] < rate * amount:
				return False, "not enough funds in sec balance " + str(self.users[userId]["balance"]["sec"]) + " less  than " + str(rate * amount)
		else:
			if not "main" in self.users[userId]["balance"]:
				return False, "not has main funds in balance to create order"
			if self.users[userId]["balance"]["main"] < amount:
				return False, "not enough funds in main balance " + str(self.users[userId]["balance"]["main"]) + " less than " + str(amount) + " look delta " + str(self.users[userId]["balance"]["main"] - amount)

		#change balance
		if orderType == "buy":
			self.users[userId]["balance"]["sec"] -= rate * amount
		else:
			self.users[userId]["balance"]["main"] -= amount

		#create order
		orderId = Exchange.nextOrderId
		Exchange.nextOrderId += 1
		self.orders[orderId] = {
			"user_id": userId,
			"create_ts": self.curTS,
			"type": orderType,
			"rate": rate,
			"amount": amount
		}

		return orderId, "order created"

	def cancelOrder(self, userId = 0, orderId = 0):
		""" отмена ордера """
		
		if not orderId in self.orders:
			return False, "Can't cancel order " + str(orderId) + ". Order not found."

		if self.orders[orderId]['user_id'] <> userId:
			return False, "Can't cancel order " + str(orderId) + ". It is not your order."

		if self.orders[orderId]["type"] == "buy":
			self.users[userId]["balance"]["sec"] += self.orders[orderId]["rate"] * self.orders[orderId]["amount"]
		else:
			self.users[userId]["balance"]["main"] += self.orders[orderId]["amount"]

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
		startTS = self.curTS - int(timeLen) * self.SEC_ID_DAY

		rows = self.dataSource.getPriceStat(startTS, self.curTS, self.pairId)

		if len(rows) > 0:
			return (rows[0][1] / rows[0][0] - rows[0][2] * rows[0][2] / rows[0][0] / rows[0][0]) ** 0.5

		return 0

	def getTotalBalance(self, userId = 0):
		""" получение последней цены согласно таймеру """
		lastPrice = self.getLastPrice()
		if not userId in self.users:
			return False, "user with id: " + str(userId) + " is not registred"

		return self.users[userId]["balance"]["sec"] + self.users[userId]["balance"]["main"] * lastPrice + sum(val["amount"] * val["rate"] for val in self.orders.values() if val["user_id"] == userId and val["type"] == "buy") + sum(val["amount"] * lastPrice for val in self.orders.values() if val["user_id"] == userId and val["type"] == "sell")

	# ================================== get trade params ================================== #
	def getMinAmount(self):
		""" get min amount in order """
		return self.minAmount

	def getFee(self):
		""" get fee """
		return self.fee

	def getPrecision(self):
		""" get precision """
		return self.precision

	def ceil(self, i, n=0):
		""" округление с отбрасыванием дробного """ 
		return int(i * 10 ** n) / float(10 ** n)
