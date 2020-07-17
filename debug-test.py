#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Temporary test script for check any things """

import misc

class Test:
	def _construct_where_conditions(self, **where):
		""" сборка where условия SQL запроса """
		if len(where) == 0:
			return " 1 = 1 "
		
		ret_array = []
		for key, val in where.items():
			if misc.isIterable(val):
				ret_array.append("%s in (%s)" % (str(key),  ", ".join(map(str, val))))
				continue
			
			if val is None:
				ret_array.append("%s is null" % str(key))
				continue
			
			ret_array.append("%s = %s" % (str(key) , str(val)))
		
		return " and ".join(ret_array)

t = Test()

print(t._construct_where_conditions(a = None))
#t._construct_where_conditions(pr = [2], s="lol")
