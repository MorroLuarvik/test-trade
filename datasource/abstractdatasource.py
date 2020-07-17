#!/usr/bin/env python
#-*-coding:utf-8-*-

class AbstractDatasource:
    """ Абстрактный источник данных """

    def get_exchanges(self):
        """ получить список бирж """
        raise NotImplementedError("Определите get_exchanges в %s." % (self.__class__.__name__))
