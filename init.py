#!/usr/bin/env python
#-*-coding:utf-8-*-
""" инициализация источников данных и подготовка модулей """

from datasource import Datasource, MySQL #normal
from configurator.configurator import get_config

Datasource.register_datasource("mysql", MySQL, get_config("mysql"))