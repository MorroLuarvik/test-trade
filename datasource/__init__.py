from .dscontrol import Datasource
from .ds1 import Ds1, DsX

Datasource().register_datasource('ds1', Ds1)
Datasource().register_datasource('dsx', DsX)

print("is register in __init__")
