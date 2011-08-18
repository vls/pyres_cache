pyres_cache
===================

`pyres_cache` is a module providing a convinient way to search/persist an iterable result.

## Feature

* Data persistence
* Indexing

## Introduction

`ResultCache` is for generic iterable result. It supports single field indexing.


`MySQLCache` is specialized for MySQLdb result. And it use sqlite memory database for memory cache. 
So it supports almost full-featured SQL query and indexing.

