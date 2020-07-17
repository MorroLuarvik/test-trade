#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Show exchange statistic data in console """

from datasource import Datasource

import init

if __name__ == "__main__":
    print("Запуск консоли")
    ds = Datasource()

    #s = 1
    #print(", ".join(map(str, s)))
    print(ds.get_exchange((1,2))) #exch_ids = (3, 2)

    #ds.get_pair
