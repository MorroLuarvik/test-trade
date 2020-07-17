#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Show exchange statistic data in console """

from datasource import Datasource

import init

if __name__ == "__main__":
    print("Запуск консоли")
    ds = Datasource()
    print(ds.get_exchange(exch_id = 3))
