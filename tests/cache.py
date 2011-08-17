#!/usr/bin/env python

import unittest
import result_cache
import sys, os
import operator
from operator import eq, ne, lt, le, ge, gt
from operator import itemgetter

class CacheTestCase(unittest.TestCase):

    save_file = 'test_save_load'

    def tearDown(self):
        for ext in ('.data', '.index'):
            try:
                os.remove(CacheTestCase.save_file + ext)
            except OSError:
                pass

    def test_save_load(self):
        data = [(1,2), (2,3), (2, 'a')]

        save_file = CacheTestCase.save_file

        cache = result_cache.ResultCache(data)

        import operator
        func = lambda x : operator.getitem(x, 0)
        cache.make_index('first', func)
        index = cache.get_index('first')

        ret = cache.save(save_file)
        self.assertEqual(ret, True)

        cache.load(save_file)
        value = cache.get_result()
        self.assertEqual(data, value)

        newindex = cache.get_index('first')
        self.assertEqual(index, newindex)

    def test_empty_load(self):
        data = range(10)
        handler = lambda : data

        cache = result_cache.ResultCache()
        cache.load_handler = handler 

        cache.load('blahblah')

        self.assertEqual(cache.get_result(), data)
        

    def test_index(self):
        data = [(1,2), (2,3), (2, 'a')]

        cache = result_cache.ResultCache(data)
        import operator
        func = lambda x : operator.getitem(x, 0)
        cache.make_index('first', func)

        index = cache.get_index('first')

        self.assertEqual(len(index), 2)
        self.assertEqual(index.keys(), [1,2])
        self.assertEqual(index[2], (2, 'a'))


        self.assertEqual(cache.get_index('blahblah'), None)



    def test_min_oper(self):
        from operator import ne, eq, lt, le, ge, gt
        cache = result_cache.ResultCache([])

        ret = cache.minimize_oper([(lt,11), (lt, 12), (le, 11), (ge, 4), (gt, 3), (gt, 4)])
        self.assertEqual(ret, [(lt, 11), (gt, 4)])

        ret = cache.minimize_oper([(lt, 1), (gt, 3)])
        self.assertEqual(ret, [])

        ret = cache.minimize_oper([(eq, 5), (lt, 1)])
        self.assertEqual(ret, [])

        ret = cache.minimize_oper([(eq, 5), (gt, 6)])
        self.assertEqual(ret, [])

        ret = cache.minimize_oper([(le, 5), (lt, 6), (ge, 5), (gt, 4)])
        self.assertEqual(ret, [(le, 5), (ge, 5)])

        ret = cache.minimize_oper([(eq, 5), (ne, 5)])
        self.assertEqual(ret, [])

    def test_get_index_dict(self):
        data = [1,4,6,3,3,8,3,2,5]
        data = [(x, i) for i, x in enumerate(data)]
        cache = result_cache.ResultCache(data)

        ret = cache.make_index("int", operator.itemgetter(0))
        self.assertEqual(ret, True)

        ret = cache.get_by_index('int', None)
        self.assertEqual(ret, [])

        ret = cache.get_by_index('int', True)
        self.assertEqual(map(itemgetter(0), ret), list(set(map(itemgetter(0), data))))

        ret = cache.get_by_index('int', lambda x: x >= 3)
        self.assertEqual(map(operator.itemgetter(0), ret), [3, 4,5,6,8])

        self.assertRaises(TypeError, lambda : cache.get_by_index('int', (lt, 4)))

        ret = cache.get_by_index('int', (eq, 3))
        self.assertEqual(ret, [(3,6)])

        ret = cache.get_by_index('int', (eq, 99))
        self.assertEqual(ret, [])

        ret = cache.get_by_index('int', (ne, 3))
        self.assertEqual(map(itemgetter(0), ret), [1, 2, 4, 5, 6, 8])


    def test_get_index_list(self):
        data = [1,4,6,3,3,8,3,2,5]
        data = [(x, i) for i, x in enumerate(data)]
        cache = result_cache.ResultCache(data)

        ret = cache.make_index("int", itemgetter(0), unique = False)
        self.assertEqual(ret, True)

        ret = cache.get_by_index('int', None)
        self.assertEqual(ret, [])

        ret = cache.get_by_index('int', True)
        self.assertEqual(list(ret), sorted(data))

        ret = cache.get_by_index('int', lambda x: x > 3)
        self.assertEqual(map(operator.itemgetter(0), ret), [4,5,6,8])

        self.assertRaises(TypeError, lambda : cache.get_by_index('int', (operator.abs, 4)))

        ret = cache.get_by_index('int', [(lt, 4), (lt, 5), (eq, 2)])
        self.assertEqual(list(ret), [(2,7)])

        ret = cache.get_by_index('int', [(lt, 4), (gt, 4)])
        self.assertEqual(ret, [])

