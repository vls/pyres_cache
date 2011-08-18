#!/usr/bin/env python
from operator import itemgetter
import decimal
D = decimal.Decimal

import MySQLdb
from MySQLdb import cursors
import sqlite3

class DataBase(object):
    def __init__(self , host = None, db = None, user = None, passwd = None, port = 3306, charset = 'utf8', multithread = False):
        self._host = host
        self._db = db
        self._user = user
        self._passwd = passwd        
        self._port   = port
        self._charset = charset

        self._conn = None
        self._cursor = None
        self._result = None

        try:
            self._conn = MySQLdb.connect(host = self._host, port = port , db=self._db, 
                user=self._user,passwd=self._passwd, use_unicode=1, charset = self._charset,
        #        cursorclass = cursors.DictCursor
                )
            self._cursor = self._conn.cursor()
        except Exception, e:
            raise e

    def __del__(self):
        if not self._conn:
            return
        try:
            self._cursor.close()
            self._conn.close()
        except Exception , e:
            self._cursor = None

    def GetAll(self, sql, parm = None ):
        try:
            self._cursor.execute(sql, parm)
            self._rows = self._cursor.fetchall()
        except Exception , e:
            raise e
        return self._rows, self._cursor.description

INT = 'INTERGER'
TEXT = 'TEXT'
TYPE_MAPPING = {
    1 : INT, # TINY
    2 : INT, # SHORT
    3 : INT, # LONG
    8 : INT, # FLOAT

    7 : 'timestamp', #timestamp
    12 : 'timestamp', #datetime

    246: 'decimal', #newdecimal

    252 : TEXT, #BLOB
    253 : TEXT, #varchar
    254 : TEXT, #string

}


def convert_type(mysql_type_code):
    global TYPE_MAPPING
    if mysql_type_code in TYPE_MAPPING:
        return TYPE_MAPPING[mysql_type_code]

    return None

def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return D(s)

sqlite3.register_adapter(D, adapt_decimal)
sqlite3.register_converter("decimal", convert_decimal)

class SQLiteDB(object):
    def __init__(self, db):
        self._db = db
        self._conn = None
        self.get_conn()

    def _connect(self):
        self._conn = sqlite3.connect(self._db, detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        
    def get_conn(self):
        if not self._conn:
            self._connect()

        if not self._conn:
            raise Exception("Can't establish a connection")

        return self._conn


    def get_create_table_sql(self, name, desc):
        
        sqlbuilder = []
        sqlbuilder.append("create table %s(" % name) 

        columns = []

        unique = set()
        for field in desc:
            type_code = field[1]
            fieldname = field[0]

            if fieldname in unique:
                fieldname += '_'
            else:
                unique.add(fieldname)

            sqlite_type = convert_type(type_code)
            if not sqlite_type:
                raise Exception("Unsupport mysql type code: %s" % type_code)

            columns.append("%s %s" % (fieldname, sqlite_type))

        sqlbuilder.append(",".join(columns))
        sqlbuilder.append(')')

        return "".join(sqlbuilder)


    def get_insert_sql(self, name, desc):
        l = len(desc)
        return 'insert into %s values (%s)' % (name, ",".join(['?'] * l))

    def dump(self, con, filename):
        with open(filename, 'w') as f:
            for line in con.iterdump():
                f.write(line)
                f.write('\n')
        

    def set_mysql_data(self, name, data, desc, syncToDisk = True):
               
        create_sql = self.get_create_table_sql(name, desc)

        con = self._conn

        insert_sql = self.get_insert_sql(name, desc)
        print insert_sql

        with con:
            con.execute(create_sql)
            con.executemany(insert_sql, data)
            
            if syncToDisk:
                self.dump(con, name+'.data')


        ret = con.execute("select * from %s" % name).fetchall()
        print ret




if __name__ == "__main__":
    mysql_db = DataBase("localhost", "gzlzh", "root", "")
    data, desc =  mysql_db.GetAll("select *, b.id as bid from testtype as a left join jointable as b on a.id = b.id")
    print data
    print desc


    sqlite_db = SQLiteDB(':memory:')
    sqlite_db.set_mysql_data("test", data, desc)
        
        
