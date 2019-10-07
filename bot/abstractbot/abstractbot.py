#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот базовые функции и всё такое """

import time

class AbstractBot:
	exchange = None
	pairId = None
	botId = None

	def __init__(self, exchange = None, pairId = 0):
		self.exchange = exchange
		self.pairId = pairId
	
	def isActiveOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 0:
			return True
		return False
	
	def isCreatedOrder(self, order):
		if 'orderId' in order:
			return True
		return False
	
	def isCompleteOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 1:
			return True
		return False

	def createOrder(self, order):
		""" создать ордер на бирже """
		orderId, error = self.exchange.createOrder(self.botId, order['type'], order['amount'], order['price'])
		if not orderId is False:
			return orderId, False
		else:
			return False, error

	def ceil(self, i, n=0):
		""" округление с отбрасыванием целого """ 
		return int(i * 10 ** n) / float(10 ** n)

	def TStoStr(self, ts = 0, format = "%Y.%m.%d %H:%M:%S"):
		return time.strftime(format, time.localtime(ts))
