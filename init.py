#!/usr/bin/env python
#-*-coding:utf-8-*-

from datasource import Datasource, MySQL
from configurator.configurator import get_config

Datasource.register_datasource("mysql", MySQL, get_config("mysql"))