#!/usr/bin/env python3
import pymysql
from sqlinj.injection import BaseInjector

class MysqlInjector(BaseInjector):

    def __init__(self):
        super().__init__()
        self.__conn = pymysql.connect(host='localhost', user='root')

    def runQuery(self, query):
        nrows = self.__conn.query(query)

        if nrows == 0:
            return False
        else:
            return True


if __name__ == '__main__':
    injector = MysqlInjector()

    databases = injector.getDatabases()
    print(databases)
    tables = injector.getTables(databases)
    print(tables)