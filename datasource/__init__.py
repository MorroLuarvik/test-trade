from .datasource import Datasource
from .mysqlds import Mysql

Datasource.register_datasource('mysql', Mysql, {})
#Datasource.register_datasource('dsx', DsX)

print("is register in __init__")
