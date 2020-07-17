#!/usr/bin/env python
#-*-coding:utf-8-*-
""" Show exchange statistic data in console """

from datasource import Datasource
from misc import TStoStr

import init

if __name__ == "__main__":
    print("Статистика по торгам в БД")
    ds = Datasource()

    for exchange in ds.get_exchange(disabled = 0):
        print()
        print(exchange['exch_name'])
        print('---------------------------------')
        for pair in ds.get_pair(exch_id = exchange['exch_id']):
            start, stop = ds.get_trades_start_ts_range(pair['pair_id'])[0].values()
            if start != stop:
                print("%s (%s): %s - %s" % (pair['pair_name'], pair['pair_id'], TStoStr(start), TStoStr(stop)))

