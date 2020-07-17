#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Temporary test script for check any things """

from configurator.configurator import get_config
from mysql import connector

connect = connector.connect(**get_config("mysql"))
#print(connect)

query = """
	select *
	from s_exchanges
"""

cursor = connect.cursor(dictionary = True)
cursor.execute(query)
print(cursor.fetchall())

print(connect.is_connected())
connect.close()