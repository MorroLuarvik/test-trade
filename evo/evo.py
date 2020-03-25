#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Класс эволюцонного процесса """

import time

class Evo:

	SEC_ID_DAY = 24 * 3600
	EVENT_STEP = 1200 # 20 min
	
	def __init__(self, exchange = None):
		if exchange is None:
			raise Exception(__file__, __name__, 'exchange not settings')

		self.exchange = exchange

	def init(self, startDate = None, stopDate = None, pairId = None, botsInGeneration = 9, generationLen = 21):
		self.startDate = self.StrToTS(startDate, "%Y.%m.%d")
		self.stopDate = self.StrToTS(stopDate, "%Y.%m.%d")
		if self.stopDate - self.startDate - self.SEC_ID_DAY < generationLen * self.SEC_ID_DAY:
			raise Exception(__file__, __name__, "generationLen: ({0}) is too large for setted startDate: ({1}) and stopDate: {2}".format(generationLen, startDate, stopDate))

		self.pairId = pairId
		self.botsInGeneration = botsInGeneration
		self.generationLen = generationLen

		print("startDate = {0}, stopDate = {1}, pairId = {2}".format(startDate, stopDate, pairId))
		pass

	def run(self, investVolume = None):
		print("Total days: {0}".format((self.stopDate - self.startDate ) / self.SEC_ID_DAY))
		print("Generation Count: {0}".format((self.stopDate - self.startDate ) / self.SEC_ID_DAY - self.generationLen))

		startDate = self.startDate
		endDate = self.startDate + self.generationLen * self.SEC_ID_DAY
		stopDate = endDate + self.SEC_ID_DAY

		for generation in range(int((self.stopDate - self.startDate ) / self.SEC_ID_DAY - self.generationLen)):
			print("generation: {0} startdate: {1} endDate: {2} stopDate: {3}".format(generation, self.TStoStr(startDate), self.TStoStr(endDate), self.TStoStr(stopDate)))
			startDate += self.SEC_ID_DAY
			endDate += self.SEC_ID_DAY
			stopDate += self.SEC_ID_DAY
		
		pass

	def report(self):
		pass

	def TStoStr(self, ts = 0, format = "%Y.%m.%d %H:%M:%S"):
		return time.strftime(format, time.localtime(ts))

	def StrToTS(self, strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
		return int(time.mktime(time.strptime(strTime, format)))
