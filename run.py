#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Основное окно """

import Tkinter as tk
import time

from localdata import LocalData

class MainWindow:
	pairId = 13
	candleWidth = 5
	marginRight = 100
	marginBottom = 30

	currentTS = None
	runnerId = None

	oldStartTs = None
	oldCandleDict = None

	def __init__(self, dbFileName, UIConfig):
		self.displayItems = {}
		self.currentTS = int(time.time())
		self._createUI(UIConfig)
		self.datasource = LocalData(dbFileName, self.pairId)

	def start(self):
		self.displayItems["root"].mainloop()
	
	def _createUI(self, config):
		self.displayItems["root"] = tk.Tk()
		self.displayItems["root"].title('Test trade')
		self.displayItems["root"].geometry('800x600')

		for item_id, params in sorted(config.items(), key = lambda item: item[1]["create_order"]):
			params["create"]["master"] = self.displayItems[params["create"]["master"]]
			self.displayItems[item_id] = getattr(tk, params["create_method"])(**params["create"])
			self.displayItems[item_id].pack(**params["pack"])
			if "binds" in params:
				for action, functionName in params["binds"].items():
					self.displayItems[item_id].bind(action, getattr(self, functionName))

		for i in ("15m", "30m", "1H", "4H", "6H", "12H", "1D", "3D"):
			self.displayItems["time_scale"].insert(tk.END, i)

		self.displayItems["start_date"].delete(0, tk.END)
		self.displayItems["start_date"].insert(0, self.TStoStr(self.currentTS))

	def testButton(self, event):
		""" тестовое событие """
		self.currentTS = self.strToTS(self.displayItems["start_date"].get())
		self.drawGraph(self.currentTS)

		return

	def runTimer(self, event):
		if self.runnerId is None:
			event.widget.config(text="Pause")
			self.runnerId = self.displayItems["root"].after(500, self.updateGraph)
		else:
			self.displayItems["root"].after_cancel(self.runnerId)
			event.widget.config(text="Play")
			self.runnerId = None

	def updateGraph(self):
		self.displayItems["start_date"].delete(0, tk.END)
		self.displayItems["start_date"].insert(0, self.TStoStr(self.currentTS))
		self.drawGraph(self.currentTS)
		self.currentTS += 300
		self.runnerId = self.displayItems["root"].after(500, self.updateGraph)

	def setCurrentTS(self, event):
		""" установка времени в ручную """
		self.currentTS = self.strToTS(self.displayItems["start_date"].get())

	def drawGraph(self, ts):
		""" отображение графика торгов """

		startTime = time.time() # ======== enter time

		canvas = self.displayItems["trade_graph"]
		canvas.delete("all")
		columns = (canvas.winfo_width() - self.marginRight) / self.candleWidth
		startTS = self.getStartTS(ts, columns, self.getTimeFrame())
		
		"""
		if startTS == self.oldStartTs:
			localTS = self.getStartTS(ts, 3, self.getTimeFrame())
			localCandleList = self.datasource.getTrades(localTS, ts, self.getTimeFrame(), self.pairId)
			localCandleDict = dict((c[3],c) for c in localCandleList)
			candleDict = self.oldCandleDict
			candleDict.update(localCandleDict)
		else:
		"""
		candleList = self.datasource.getTrades(startTS, ts, self.getTimeFrame(), self.pairId)
		candleDict = dict((c[3],c) for c in candleList)

		startDrawTime = time.time() # ======== draw time

		if len(candleDict) == 0:
			print("not info for print")
			return
		minPrice = min((candleDict[key][0] for key in candleDict))
		maxPrice = max((candleDict[key][1] for key in candleDict))
		
		for dispalyTS in range(startTS, ts, self.getTimeFrame()):
			candle = None
			if dispalyTS in candleDict:
				candle = candleDict[dispalyTS]
			self.drawCandle(canvas, (dispalyTS - startTS) / self.getTimeFrame() * self.candleWidth + 1, minPrice, maxPrice, candle)

		#self.oldCandleDict = candleDict
		#self.oldStartTs = startTS

		self.drawPriceScale(canvas, minPrice, maxPrice)

		print('get data time:' + str(startDrawTime - startTime))
		print('draw time:' + str(time.time() - startDrawTime)) # ======== report time

	def drawPriceScale(self, canvas, minPrice, maxPrice):
		""" отображение шкалы цен """

		priceDelta = maxPrice - minPrice

		# ====================== тестируем отображение текста ====================== #
		canvas = self.displayItems["trade_graph"]
		canvas.create_text(100, 100, text="price delta: {0}".format(priceDelta),  justify=tk.LEFT) #, font="Verdana 14"
		# ====================== тестируем отображение текста ====================== #

		pass

	def drawCandle(self, canvas, x, minPrice, maxPrice, candleInfo):
		""" рисуем свечку """
		topY = 0
		bottomY = canvas.winfo_height() - self.marginBottom
		
		canvas.create_rectangle(x, topY, x+3, bottomY, outline="#fff", fill="#fff")
		if candleInfo is None:
			return

		canvas.create_line(x + 2, self.priceToY(topY, bottomY, maxPrice, minPrice, candleInfo[0]), x + 2, self.priceToY(topY, bottomY, maxPrice, minPrice, candleInfo[1]))
		fill = "#000"
		if candleInfo[4] < candleInfo[5]:
			fill = "#fff"
		canvas.create_rectangle(x+1, self.priceToY(topY, bottomY, maxPrice, minPrice, candleInfo[4]), x+3, self.priceToY(topY, bottomY, maxPrice, minPrice, candleInfo[5]), outline="#000", fill=fill)

	def priceToY(self, topY, bottomY, maxPrice, minPrice, price):
		return int(topY + (maxPrice - price) / (maxPrice - minPrice) * (bottomY - topY))


	def getTimeFrame(self):
		""" возвращает выбранный таймфрейм в секундах """
		timeFrameName = self.displayItems["time_scale"].get(tk.ACTIVE)

		if timeFrameName == '15m':
			return 15 * 60
		if timeFrameName == '30m':
			return 30 * 60
		if timeFrameName == '1H':
			return 3600
		if timeFrameName == '4H':
			return 4 * 3600
		if timeFrameName == '6H':
			return 6 * 3600
		if timeFrameName == '12H':
			return 12 * 3600
		if timeFrameName == '1D':
			return 24 * 3600
		if timeFrameName == '3D':
			return 24 * 3 * 3600
		
		return 3600

	def getStartTS(self, ts, columns, timeFrame):
		""" возвращает стартовый TS в зависимости от ширины графика """
		startTs = ts - columns * timeFrame
		return (startTs / int(timeFrame)) * int(timeFrame)


	def strToTS(self, strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
		return int(time.mktime(time.strptime(strTime, format)))
	
	def TStoStr(self, ts = 0, format = "%Y.%m.%d %H:%M:%S"):
		return time.strftime(format, time.localtime(ts))



if __name__ == "__main__":
	DB_DIR = 'db'
	DB_NAME = 'database.db'

	RES_DIR = 'res'
	WINDOW_RES_NAME = 'window_config.json'

	import os
	dirName, fileName = os.path.split(os.path.abspath(__file__))

	dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME
	resFileName = dirName + os.path.sep + RES_DIR +  os.path.sep + WINDOW_RES_NAME

	import json
	file = open(resFileName, 'r+')
	windowConfig = json.load(file)
	file.close()


	mw = MainWindow(dbFileName, windowConfig)
	mw.start()

print("Bye!")
