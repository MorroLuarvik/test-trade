#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Источник данных """

from .abstractdatasource import AbstractDatasource

class Datasource(AbstractDatasource):
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
	def get_exchange(self, **params):
		""" получение списка бирж get_exchange(exch_id = None)"""
		if not self._has_active_datasource():
			self._activate_datasource(self.selected_datasource)

		return self.datasource_list[self.selected_datasource]["object"].get_exchange(**params)
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
		""" включение активного источника данных """
		self.selected_datasource = key
		self.datasource_list[self.selected_datasource]["object"] = self.datasource_list[self.selected_datasource]["class"](**self.datasource_list[self.selected_datasource]["config"])

