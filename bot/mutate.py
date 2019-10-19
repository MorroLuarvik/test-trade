#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Механизм мутации параметров каскада. Эволюция здесь. """

import random

class Mutate:

	weightParams = {'profitPercent': .5}

	def setWeightParams(self, weightParams):
		""" настройка весовых параметров """
		self.weightParams = weightParams

	def getWeight(self, bot, bots):
		""" получение веса """
		weight = 0
		for paramName in self.weightParams:
			minVal = min([item[paramName] for item in bots])
			valRange = max([item[paramName] for item in bots]) - minVal
			if valRange == 0:
				continue
			weight += (bot[paramName] - minVal) * self.weightParams[paramName] / valRange 

		return weight



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
			ret[key] = self._getRandomParam(item)

		return ret

	def mutateParams(self, paramsTemplate, params, qty = 1):
		""" изменение случайных параметров в указанном количестве """
		
		mutateKeys = []
		for key in paramsTemplate:
			if paramsTemplate[key]['mutable']:
				mutateKeys.append(key)

		for cou in range(qty):
			curKey = mutateKeys[random.randint(0, len(mutateKeys) - 1)]
			params[curKey] = self._getRandomParam(paramsTemplate[curKey])

		return params

	def fusionParams(self, paramsTemplate, params1, params2):
		""" слияние параметров """
		ret = {}
		for key in paramsTemplate:
			if not paramsTemplate[key]['mutable']:
				ret[key] = paramsTemplate[key]['default']
				continue
			if random.randint(0, 1) == 0:
				ret[key] = params1[key]
			else:
				ret[key] = params2[key]
		
		return ret

	def _getRandomParam(self, paramTemplate):
		""" generate random param """
		if paramTemplate['mutable']:
			randomizeFunction = '_randomizeFloat' #getattr(self, '__randomizeFloat')
			if paramTemplate['type'] == 'int':
				randomizeFunction = '_randomizeInt' #getattr(self, '__randomizeInt')
			if paramTemplate['type'] == 'bool':
				randomizeFunction = '_randomizeBool' #getattr(self, '__randomizeBool')
			
			ret = getattr(self, randomizeFunction)(paramTemplate['min'], paramTemplate['max'])
		else:
			ret = paramTemplate['default']
		
		return ret


	def _randomizeInt(self, minVal, maxVal):
		return int(minVal + (maxVal - minVal) * random.random())

	def _randomizeFloat(self, minVal, maxVal, pers = 4):
		return round(float(minVal + (maxVal - minVal) * random.random()), pers)

	def _randomizeBool(self, minVal = False, maxVal = True):
		if random.randint(0, 1) == 0:
			return False

		return True
