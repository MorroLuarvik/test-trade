#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Temporary test script for check any things """

SEC_ID_DAY = 24 * 3600

import time

def TStoStr(ts = 0, format = "%Y.%m.%d %H:%M:%S"):
	return time.strftime(format, time.localtime(ts))

def StrToTS(strTime = "2018.09.01 00:00:00", format = "%Y.%m.%d %H:%M:%S"):
	return int(time.mktime(time.strptime(strTime, format)))

startTS = StrToTS("2018.11.01 00:00:00")
print(TStoStr(startTS + SEC_ID_DAY))