#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Источник данных """

from .abstractdatasource import AbstractDatasource

class Datasource(AbstractDatasource): # наследование от абстрактного класса источника данных сделано для отображения всплывающих подсказок
	""" Источник данных """
	
	datasource_list = {}
	selected_datasource = None

	@classmethod
	def register_datasource(cls, key: str, datasource: AbstractDatasource, config = {}):
		""" Регистрация источника данных """
		cls.datasource_list[key] = {"class": datasource, "config": config}
		cls.selected_datasource = key

	def get_current_datasource(self):
		""" возвращает активный источник данных """
		return self.selected_datasource

	def switch_datasource(self, key: str):
		""" смена источника данных """
		if not key in self.datasource_list.keys():
			raise Exception("Выбран незарегистрированный источник данных")

		self._disable_active_datasource()
		self._activate_datasource(key)

	# ----------------------------- интерфейс функций разных реализаций источников данных ----------------------------- #
	def __getattribute__(self, name):
		""" перехват вызова любой функции """
		if name not in [arg for arg in dir(AbstractDatasource) if not arg.startswith('_')]:
			return super().__getattribute__(name) # метод не входит в абстрактный класс источника данных, значит просто его выполняем
		
		if not self._has_active_datasource():
			self._activate_datasource(self.selected_datasource)
		
		def _wrapper(*args, **kwargs): 
			""" передача параметров текущему источнику данных """
			return getattr(self.datasource_list[self.selected_datasource]["object"], name)(*args, **kwargs)

		return _wrapper # вызов метода в текущем источнике данных
	# ----------------------------- интерфейс функций разных реализаций источников данных ----------------------------- #

	def _has_active_datasource(self): 
		""" проверка наличия активного источника данных """
		if "object" in self.datasource_list[self.selected_datasource]:
			return isinstance(self.datasource_list[self.selected_datasource]["object"], self.datasource_list[self.selected_datasource]["class"])

		return False

	def _disable_active_datasource(self):
		""" отключение активного источника данных """
		del(self.datasource_list[self.selected_datasource]["object"])

	def _activate_datasource(self, key: str):
		""" включение указанного источника данных """
		self.selected_datasource = key
		self.datasource_list[self.selected_datasource]["object"] = self.datasource_list[self.selected_datasource]["class"](**self.datasource_list[self.selected_datasource]["config"])

