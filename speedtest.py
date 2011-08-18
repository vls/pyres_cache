#!/usr/bin/env python
import time, functools

def timeit(func): 
    @functools.wraps(func) 
    def __do__(*args,**kwargs): 
        start = time.time() 
        result= func(*args,**kwargs) 
        print '%s used time %ss'%(func.__name__,time.time()-start) 
        return result 
    return __do__ 



from result_cache.MySQLCache import DataBase, SQLiteDB

@timeit
def test_insert(db, name, data, desc):
    
    db.set_mysql_data(name, data, desc, False)

def test_mysql_cache():
    mysql_db = DataBase("localhost", "gzlzh", "root", "")
    data, desc =  mysql_db.GetAll("select *, b.id as bid from testtype as a left join jointable as b on a.id = b.id")

    sqlite_db = SQLiteDB(':memory:')
    name = "test"
    sqlite_db.create_table(name, desc)

    data = data * 10000
    test_insert(sqlite_db, name, data,desc)


def main():
    test_mysql_cache()

if __name__ == "__main__":
    main()
