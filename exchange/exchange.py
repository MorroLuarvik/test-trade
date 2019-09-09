#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Симулятор биржы """

class Exchange:

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
		self.nextUserId = 0
		self.nextOrderId = 0
		self.users = {}
		self.orders = {}

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
			self.users[userId]["balance"]["main"] = funds
			return True, "funds for user with id: " + str(userId) + " added succesyfull"

		self.users[userId]["balance"]["main"] += funds
		return True, "funds for user with id: " + str(userId) + " added succesyfull"
