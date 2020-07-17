#!/usr/bin/env python
#-*-coding:utf-8-*-

from .abstractdatasource import AbstractDatasource
from mysql import connector

class MySQL(AbstractDatasource):
    """ Источник данных MySQL """
