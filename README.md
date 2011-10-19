pyres_cache
===================

`pyres_cache` is a module providing a convinient way to search/persist an iterable result.

## Feature

* Data persistence
* Data in-memory caching
* Indexing
* Quering

## Introduction

`ResultCache` is for generic iterable result. It supports single field indexing.


`MySQLCache` is specialized for MySQLdb result. And it use sqlite memory database for memory cache. 
So it supports almost full-featured SQL query and indexing.

## Usage

Just place the source file into your source folder and import it!

## Example


    mysql_db = DataBase("localhost", "somedb", "root", "")
    sql = "select *, b.id as bid from testtype as a left join jointable as b on a.id = b.id"
    sqlite_db = SQLiteDB(':memory:')

    name = "test"
    sqlite_db.load(name, import_from_mysql(name, mysql_db, sql))

    print sqlite_db.GetAll("select * from %s" % name)
