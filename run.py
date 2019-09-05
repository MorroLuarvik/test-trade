#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Основное окно """

import Tkinter as tk
import time

class MainWindow:
	pairId = 13
	candleWidth = 4
	magrinRight = 100
	marginBottom = 30

	def __init__(self):
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
			"test_button": {
				"create_order": 30,
				"create_method": "Button",
				"create": {
					"master": "root", 
					"text": "Test",
				},
				"pack": {
				}
			}
		}
		self._createUI(UIConfig)

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

	def testButton(self, event):
		""" тестовое событие """
		print(self.displayItems["trade_graph"].winfo_width())
		self.displayItems["trade_graph"].create_line(0, 0, 200, 100)

		self.drawGraph(time.time())

		#print(event.widget)

	def drawGraph(self, ts):
		""" отображение графика торгов """
		canvas = self.displayItems["trade_graph"]
		columns = (canvas.winfo_width() - self.magrinRight) / self.candleWidth
		print("columns :{0}".format(columns))
		print((31 / int(10)) * 10) # округление меньшего значения
	
	def getTimeFrame(self):
		""" возвращает выбранный таймфрейм в секундах """
		pass

	def getStartTS(self, ts):
		""" возвращает стартовый TS в зависимости от ширины графика """
		pass

	def StrToTS(self, strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
		return int(time.mktime(time.strptime(strTime, format)))



if __name__ == "__main__":
	mw = MainWindow()
	mw.start()

print("Bye!")
