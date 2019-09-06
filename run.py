#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Основное окно """

import Tkinter as tk
import time

from localdata import LocalData

class MainWindow:
	pairId = 13
	candleWidth = 4
	marginRight = 100
	marginBottom = 30

	currentTS = None

	def __init__(self, dbFileName):
		self.displayItems = {}
		UIConfig = {
			"time_scale": {
				"create_order": 10,
				"create_method": "Listbox",
				"create": {
					"master": "root", 
					"width": "5",
					"selectmode": "single"
				},
				"pack": {
					"side": "left",
					"anchor": "nw"
				}
			},
			"trade_graph": {
				"create_order": 20,
				"create_method": "Canvas",
				"create": {
					"master": "root", 
					"bg": "white",
					"height": "400"
				},
				"pack": {
					"side": "top",
					"fill": "x" 
				}
			}, 
			"start_date": {
				"create_order": 30,
				"create_method": "Entry",
				"create": {
					"master": "root" 
				},
				"pack": {
					"side": "left",
					"anchor": "nw"
				}
			},
			"set_button": {
				"create_order": 40,
				"create_method": "Button",
				"create": {
					"master": "root", 
					"text": "Set",
				},
				"pack": {
					"side": "left",
					"anchor": "nw"
				}
			},
			"test_button": {
				"create_order": 300,
				"create_method": "Button",
				"create": {
					"master": "root", 
					"text": "Test",
				},
				"pack": {
				}
			}
		}
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

		for i in ("15m", "30m", "1H", "4H", "6H", "12H", "1D", "3D"):
			self.displayItems["time_scale"].insert(tk.END, i)

		self.displayItems["test_button"].bind("<Button-1>", self.testButton)
		self.displayItems["start_date"].delete(0, tk.END)
		self.displayItems["start_date"].insert(0, self.TStoStr(self.currentTS))
		self.displayItems["set_button"].bind("<Button-1>", self.setCurrentTS)

	def testButton(self, event):
		""" тестовое событие """
		self.currentTS = self.strToTS(self.displayItems["start_date"].get())
		self.drawGraph(self.setCurrentTS)
		return

	def setCurrentTS(self, event):
		""" установка времени в ручную """
		self.currentTS = self.strToTS(self.displayItems["start_date"].get())

	def drawGraph(self, ts):
		""" отображение графика торгов """
		canvas = self.displayItems["trade_graph"]
		columns = (canvas.winfo_width() - self.marginRight) / self.candleWidth

		startTS = self.getStartTS(self.currentTS, columns, self.getTimeFrame())
		candleList = self.datasource.getTrades(startTS, self.currentTS, self.getTimeFrame(), self.pairId)
		if len(candleList) == 0:
			print("not info for print")
			return
		minPrice = min((c[0] for c in candleList))
		maxPrice = max((c[1] for c in candleList))
		candleDict = dict((c[3],c) for c in candleList)
		for dispalyTS in range(startTS, self.currentTS, self.getTimeFrame()):
			candle = None
			if dispalyTS in candleDict:
				candle = candleDict[dispalyTS]
			self.drawCandle(canvas, (dispalyTS - startTS) / self.getTimeFrame() * self.candleWidth, minPrice, maxPrice, candle)

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

	import os
	dirName, fileName = os.path.split(os.path.abspath(__file__))

	dbFileName = dirName + os.path.sep + DB_DIR +  os.path.sep + DB_NAME
	mw = MainWindow(dbFileName)
	mw.start()

print("Bye!")
