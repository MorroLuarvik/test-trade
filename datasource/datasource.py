#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Источник данных """

class Datasource():
    """ Источник данных """
    
    datsource_list = []

    def register_datasource(self, datasource):
        self.datsource_list.append(datasource)

