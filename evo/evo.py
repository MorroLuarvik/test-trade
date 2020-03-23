#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Класс эволюцонного процесса """

import time

class Evo:
	
	def __init__(self, exchange = None):
		if exchange is None:
			raise Exception(__file__, __name__, 'exchange not settings')

		self.exchange = exchange

	def init(self, startDate = None, stopDate = None, pairId = None, botsInGeneration = 9, generationLen = 30):
		print("startDate = {0}, stopDate = {1}, pairId = {2}".format(startDate, stopDate, pairId))
		pass

	def run(self):
		pass

	def report(self):
		pass

	def TStoStr(self, ts = 0, format = "%Y.%m.%d %H:%M:%S"):
		return time.strftime(format, time.localtime(ts))

	def StrToTS(self, strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
		return int(time.mktime(time.strptime(strTime, format)))
