#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Механизм мутации параметров каскада. Эволюция здесь. """

import random

class Mutate:

	def getDefaultParams(self, paramsTemplate):
		""" получаем параметры по умолчанию """
		ret = {}
		for key, item in paramsTemplate.items():
			ret[key] = item['default']
		return ret

	def getRandomParams(self, paramsTemplate):
		""" получаем ВСЕ случайные параметры """
		ret = {}
		for key, item in paramsTemplate.items():
			if item['mutable']:
				randomizeFunction = '_randomizeFloat' #getattr(self, '__randomizeFloat')
				if item['type'] == 'int':
					randomizeFunction = '_randomizeInt' #getattr(self, '__randomizeInt')
				if item['type'] == 'bool':
					randomizeFunction = '_randomizeBool' #getattr(self, '__randomizeBool')
				
				ret[key] = getattr(self, randomizeFunction)(item['min'], item['max'])
			else:
				ret[key] = item['default']

		return ret

	def mutateParams(self, paramsTemplate, params, qty = 1):
		""" изменение случайных параметров в указанном количестве """
		return params

	def fusionParams(self, params1, params2):
		""" слияние параметров """
		ret = {}
		for key in params1:
			if random.randint(0, 1) == 0:
				ret[key] = params1[key]
			else:
				ret[key] = params2[key]
		
		return ret

	def _randomizeInt(self, minVal, maxVal):
		return int(minVal + (maxVal - minVal) * random.random())

	def _randomizeFloat(self, minVal, maxVal, pers = 4):
		return round(float(minVal + (maxVal - minVal) * random.random()), pers)

	def _randomizeBool(self, minVal = False, maxVal = True):
		if random.randint(0, 1) == 0:
			return False

		return True
