#!/usr/bin/env python

import sys, os
import marshal
import operator
import itertools
from operator import eq, ne, lt, le, gt, ge
from operator import itemgetter
from bisect import bisect_left, bisect_right

class ResultCache(object):
    def __init__(self, rs = None):
        self._result_set = rs
        self._load_handler = None
        self._index = {}

    def save(self, filename, overwrite = True):
        count = 1
        while not overwrite and os.path.exists(filename):
            filename = "%s.%d" % (filename, count)
            count += 1

        with open(filename+'.data', 'wb') as f:
            ret = marshal.dump(self._result_set, f)

        with open(filename+'.index', 'wb') as f:
            marshal.dump(self._index, f)
        return True

    def load(self, filename):
        datafile = filename+'.data'
        if os.path.exists(datafile):
            with open(filename+'.data', 'rb') as f:
                value = marshal.load(f)
                self._result_set = value
        else:
            if self._load_handler and callable(self._load_handler):
                self._result_set = self._load_handler()

        indexfile = filename+'.index'
        if os.path.exists(indexfile):
            with open(filename+'.index', 'rb') as f:
                self._index = marshal.load(f)

        return self

    def set_load_handler(self, value):
        self._load_handler = value

    load_handler = property(fset = set_load_handler)

    def get_result(self):
        return self._result_set

    def make_index(self, index_name, get_func = None, unique = True, reverse = False):

        if unique:
            index = {}
            if get_func is None or not callable(get_func):
                for row in self._result_set:
                    index[row] = row

            else:
                for row in self._result_set:
                    key = get_func(row)
                    index[key] = row
        else:
            keyrowlist = [ (get_func(row), row) for row in self._result_set]

            index = sorted(keyrowlist, reverse = reverse)


        self._index[index_name] = index

        return True

    def get_index(self, index_name):
        return self._index.get(index_name, None)


    def get_by_index_dict(self, index, value_spec):
        if callable(value_spec):
            return (v for k,v in index.iteritems() if value_spec(k))

        if not value_spec:
            return []

        if value_spec == True:
            return (v for _,v in index.iteritems())
        
        if isinstance(value_spec, list):
            oper, value = value_spec[0]
        elif isinstance(value_spec, tuple):
            oper, value = value_spec
        else:
            raise TypeError("value_spec must either type 'list' or type 'tuple'")

        if oper not in (eq, ne):
            raise TypeError("unique index only support == and != operator")

        if oper is eq:
            row = index.get(value, None)
            if row:
                return [row]
            else:
                return []
        else:
            #assume oper = ne
            return (v for k,v in index.iteritems() if k != value)

    def get_by_index_list(self, index, value_spec):

        if callable(value_spec):
            return (v for key, v in index if value_spec(key))

        if not value_spec:
            return []

        if value_spec is True:
            return (v for _, v in index)

        opers = map(itemgetter(0), value_spec)

        for oper in opers:
            if oper not in (eq, ne, lt, le, ge, gt):
                raise TypeError("only support ==, !=, <, <=, >, >= operator")

        value_spec = self.minimize_oper(value_spec)

        if not value_spec:
            return []

        operdict = dict(value_spec)
        
        indexkey = map(itemgetter(0), index)

        if eq in operdict:
            value = operdict[eq]
            start = bisect_left(indexkey, value)
            end = bisect_right(indexkey, value)
            return (index[i][1] for i in xrange(start, end))

        start = 0
        end = len(index)

        if lt in operdict or le in operdict:
            if lt in operdict:
                lfunc = lt
                func = bisect_left
            else:
                lfunc = le
                func = bisect_right

            value = operdict[lfunc]
            new_end = func(indexkey, value)

            if new_end <= end:
                end = new_end

        if gt in operdict or ge in operdict:
            if gt in operdict:
                lfunc = gt
                func = bisect_right
            else:
                lfunc = ge
                func = bisect_left

            value = operdict[lfunc]
            new_start = func(indexkey, value)

            if new_start > start:
                start = new_start

        gen = (index[i][1] for i in xrange(start, end))

        if eq in operdict:
            value = operdict[eq]
            gen = (x for x in gen if x == value)
        
        if ne in operdict:
            value = operdict[ne]
            gen = (x for x in gen if x != value)

        return gen


    def get_by_index(self, index_name, value_spec):
        
        if not self._index.has_key(index_name):
            raise KeyError('No index named [%s]' % index_name)


        index = self._index[index_name]

        if isinstance(index, dict):
            return self.get_by_index_dict(index, value_spec)
            
        elif isinstance(index, list):
            return self.get_by_index_list(index, value_spec)
            


    def minimize_oper(self, value_spec):

        other_spec = [(oper, value) for oper, value in value_spec if oper not in (eq, ne, lt, le, ge, gt)]
        new_value_spec = []
        for oper, glist in itertools.groupby(value_spec, itemgetter(0)):
            glist = list(glist)
            if oper is eq:
                if len(glist) > 1:
                    return other_spec

                new_value_spec.extend(glist)

            elif oper is ne:
                new_value_spec.extend(glist)

            elif oper in (lt, le, gt, ge):
                if oper in (lt, le):
                    func = min
                else:
                    func = max

                if len(glist) > 1:
                    new_value_spec.append((oper, func(map(itemgetter(1), glist))))
                else:
                    # len(glist) == 1
                    new_value_spec.extend(glist)

        operdict = dict(new_value_spec)

        if lt in operdict and le in operdict:
            if operdict[lt] <= operdict[le]:
                del operdict[le]
            else:
                del operdict[lt]

        if gt in operdict and ge in operdict:
            if operdict[gt] >= operdict[ge]:
                del operdict[ge]
            else:
                del operdict[gt]

        """
        [(eq, 5), (ne, 5)] => []
        """
        if eq in operdict and ne in operdict:
            if operdict[eq] == operdict[ne]:
                return other_spec
    
        if eq in operdict and (lt in operdict or le in operdict or gt in operdict or ge in operdict):
            lambda_list = []
            if lt in operdict:
                lambda_list.append(lambda x: x[lt] <= x[eq])
            if le in operdict:
                lambda_list.append(lambda x: x[le] < x[eq])
            if gt in operdict:
                lambda_list.append(lambda x: x[gt] >= x[eq])
            if ge in operdict:
                lambda_list.append(lambda x: x[ge] > x[eq])

            flag = any(map(lambda f: f(operdict), lambda_list))

            if flag:
                return other_spec

        if (lt in operdict or le in operdict) and (gt in operdict or ge in operdict):
            lfunc = lt if lt in operdict else le
            gfunc = gt if gt in operdict else ge

            if operdict[lfunc] < operdict[gfunc]:
                return other_spec

            if operdict[lfunc] == operdict[gfunc] and not (lfunc == le and gfunc == ge ):
                return other_spec
            

        other_spec.extend(operdict.items())
        return other_spec





        
        


            

        
        



        
        
    
    
