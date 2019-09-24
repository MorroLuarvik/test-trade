#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Абстрактный бот базовые функции и всё такое """

class AbstractBot:
	exchange = None
	pairId = None

	def __init__(self, exchange = None, pairId = 0):
		print("init abstract")
		self.exchange = exchange
		self.pairId = pairId
