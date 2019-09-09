#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Симулятор биржы """

class Exchange:

	fee = 0.2
	minPrice = 1e-8
	maxPrice = 1
	minAmount = 0.5

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
		self.users = {}
		self.orders = {}

	def setTS(self, ts = None):
		""" установка времени сервера """
		if not self.curTS is None:
			self._executeOrders(self.curTS, ts)
		self.curTS = ts

	def _executeOrders(self, startTS, endTs):
		""" выполнение ордеров """

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

		if not "sec" in self.users[userId]["balance"]:
			self.users[userId]["balance"]["sec"] = funds
			return True, "funds for user with id: " + str(userId) + " added successfull"

		self.users[userId]["balance"]["sec"] += funds
		return True, "funds for user with id: " + str(userId) + " added successfull"

	def createOrder(self, userId = 0, orderType = "buy", rate = 0, amount = 0):
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
			if self.users[userId]["balance"]["main"] < rate:
				return False, "not enough funds in main balance " + str(self.users[userId]["balance"]["main"]) + " less than " + str(rate)

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
			"amount": amount
		}

		return orderId