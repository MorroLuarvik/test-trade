#!/usr/bin/env python
#-*-coding:utf-8-*-

from datasource import Datasource, MySQL

Datasource.register_datasource('mysql', MySQL, {})