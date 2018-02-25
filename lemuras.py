__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'aivanf@mail.ru'
__version__ = '1.0.4'
__license__ = """License:
 This software is provided 'as-is', without any express or implied warranty.
 You may not hold the author liable.

 Permission is granted to anyone to use this software for any purpose,
 including commercial applications, and to alter it and redistribute it freely,
 subject to the following restrictions:

 The origin of this software must not be misrepresented. You must not claim
 that you wrote the original software. When use the software, you must give
 appropriate credit, provide a link to the original file, and indicate if changes were made.
 This notice may not be removed or altered from any source distribution."""

import sys

if sys.version_info[0] == 2:
    from io import BytesIO
    file_container = lambda x: BytesIO(bytes(x))

else:
    from io import StringIO
    file_container = lambda x: StringIO(x)


def iscollection(x):
    return isinstance(x, list) or isinstance(x, tuple)


def tryInt(x):
    try:
        return int(x)
    except:
        return None


def tryFloat(x):
    try:
        return float(x)
    except:
        return None


def listOfLists(cnt):
    res = []
    for i in range(cnt):
        res.append([])
    return res


def mode(lst):
    return max(set(lst), key=lst.count)


def median(lst):
    n = len(lst)
    if n < 1:
        return None
    if n % 2 == 1:
        return sorted(lst)[n // 2]
    else:
        return sum(sorted(lst)[n // 2 - 1:n // 2 + 1]) / 2.0


def avg(lst):
    return 1.0 * sum(lst) / len(lst)


aggfuns = {
    'avg': avg,
    'mean': avg,
    'mode': mode,
    'middle': median,
    'median': median,
    'count': len,
    'sum': sum,
    'min': min,
    'max': max,
}


class Column(object):
    def __init__(self, values):
        self.values = values

    @classmethod
    def make(cls, size, value=None):
        return Column([value] * size)

    def isin(self, other):
        """Returns new Column object with boolean whether the current values are in other object.
        The other object may be a list, a Column, or anything else with .__contains__ method."""
        res = []
        for a in self.values:
            v = False
            for b in other:
                if a == b:
                    v = True
                    break
            res.append(v)
        return Column(res)

    def lengths(self):
        """Returns new Column object with applied len to current values."""
        res = []
        for el in self.values:
            res.append(len(el))
        return Column(res)

    def count(self):
        """Returns count of true values."""
        res = 0
        for el in self.values:
            if el:
                res += 1
        return res

    def __repr__(self):
        n = len(self.values)
        ns = False
        if n > 12:
            n = 10
            ns = True
        res = '- Column object, values: ' + str(self.values[:n]) + '.'
        if ns:
            res += ' . .'
        return res

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)

    def __contains__(self, item):
        for el in self.values:
            if el == item:
                return True
        return False

    def __and__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] and other[i])
                return Column(res)
            else:
                raise ValueError('Column.__and__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el and other)
            return Column(res)

    def __or__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] or other[i])
                return Column(res)
            else:
                raise ValueError('Column.__or__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el or other)
            return Column(res)

    def __add__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] + other[i])
                return Column(res)
            else:
                raise ValueError('Column.__add__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el + other)
            return Column(res)

    def __sub__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] - other[i])
                return Column(res)
            else:
                raise ValueError('Column.__sub__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el - other)
            return Column(res)

    def __mul__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] * other[i])
                return Column(res)
            else:
                raise ValueError('Column.__mul__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el * other)
            return Column(res)

    def __mod__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] % other[i])
                return Column(res)
            else:
                raise ValueError('Column.__mod__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el % other)
            return Column(res)

    def __truediv__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] / other[i])
                return Column(res)
            else:
                raise ValueError('Column.__truediv__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el / other)
            return Column(res)

    def __div__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] / other[i])
                return Column(res)
            else:
                raise ValueError('Column.__div__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el / other)
            return Column(res)

    def __gt__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] > other[i])
                return Column(res)
            else:
                raise ValueError('Column.__gt__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el > other)
            return Column(res)

    def __lt__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] < other[i])
                return Column(res)
            else:
                raise ValueError('Column.__lt__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el < other)
            return Column(res)

    def __ge__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] >= other[i])
                return Column(res)
            else:
                raise ValueError('Column.__ge__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el >= other)
            return Column(res)

    def __le__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] <= other[i])
                return Column(res)
            else:
                raise ValueError('Column.__le__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el <= other)
            return Column(res)

    def __eq__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] == other[i])
                return Column(res)
            else:
                raise ValueError('Column.__eq__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el == other)
            return Column(res)

    def __ne__(self, other):
        if isinstance(other, Column):
            la = len(self.values)
            lb = len(other)
            if lb == la:
                res = []
                for i in range(la):
                    res.append(self.values[i] != other[i])
                return Column(res)
            else:
                raise ValueError('Column.__ne__ others Column len must be the same')
        else:
            res = []
            for el in self.values:
                res.append(el != other)
            return Column(res)


class Grouped(object):
    def __init__(self, keys, columns, column_indices):
        self.keys = keys
        self.count = len(keys)
        self.fun = None

        # Columns indices of keys in original columns
        self.gun = []
        for el in keys:
            self.gun.append(column_indices[el])

        # Columns names of grouped rows
        self.columns = {}
        # If old indices should be saved
        self.column_indices = []
        step = 0
        for cur in columns:
            if cur not in keys:
                self.column_indices.append(True)
                self.columns[cur] = step
                step += 1
            else:
                self.column_indices.append(False)

        # Dict of dict of ... of list with grouped rows
        if self.count > 0:
            self.values = {}
        else:
            self.values = listOfLists(len(self.columns))

    def add(self, row):
        vals = self.values
        for i in range(self.count):
            last = i == self.count - 1
            ind = self.gun[i]
            cur = row[ind]
            if cur not in vals:
                if last:
                    # store columns independently
                    vals[cur] = listOfLists(len(self.columns))
                else:
                    vals[cur] = {}
            vals = vals[cur]

        # Save values with appropriate indices only - without keys
        step = 0
        for i in range(len(row)):
            if self.column_indices[i]:
                # Columns-first structure
                vals[step].append(row[i])
                step += 1

    def __agglist__(self, keys, cols):
        """Applies aggregation functions on given group."""
        res = keys
        for target_name in self.fun:
            cur_col = cols[self.columns[target_name]]
            for new_name in self.fun[target_name]:
                task = self.fun[target_name][new_name]
                if isinstance(task, str):
                    res.append(aggfuns[task](cur_col))
                else:
                    res.append(task(cur_col))
        return res

    def __recurs__(self, vals, keys, task):
        """Recursive method to move through grouping keys."""
        res = []
        if isinstance(vals, dict):
            for key in vals:
                res.extend(self.__recurs__(vals[key], keys + [key], task))
        elif iscollection(vals):
            res.append(task(keys, vals))
        return res

    def agg(self, fun):
        """Returns new Table object from aggregated groups.
        The argument must be a dictionary where keys are old columns names,
        and the values are other dictionaries where keys are new columns names,
        and the values are strings with aggregation functions names or function or lambdas."""
        self.fun = fun
        cols = self.keys
        for target_name in fun:
            for new_name in fun[target_name]:
                cols.append(new_name)
        rows = self.__recurs__(self.values, [], self.__agglist__)
        return Table(cols, rows)

    def counts(self):
        """Returns new Table object with counts of the groups."""
        rows = []
        todo = lambda x, y: rows.append(x + [len(y[0])])
        self.__recurs__(self.values, [], todo)
        return Table(self.keys + ['counts'], rows)

    def _repr_html_(self):
        res = '<b>Grouped</b> object, old columns: ' + str(list(self.columns.keys())) + '.<br>'
        res += self.counts().html()
        return res

    def __repr__(self):
        res = '- Grouped object, keys: ' + str(self.keys) + ', old columns: ' + str(list(self.columns.keys())) + '.'
        return res


class Table(object):
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.colcnt = len(self.columns)
        self.rowcnt = len(self.rows)
        self.column_indices = {}
        for i in range(len(self.columns)):
            self.column_indices[self.columns[i]] = i

    @classmethod
    def fromCsv(cls, data, inline=False):
        """Returns new Table object from CSV data.
        If inline is False (default), then the first argument is considered
        as a string with name of a file where the CSV data is located.
        Otherwise, the first argument is considered as a string with CSV data itself."""
        rows = []
        if inline:
            f = file_container(data)
        else:
            f = open(data)
        with f:
            for line in f:
                line = line.replace('\n', '')
                cur = line.split(',')
                for i in range(len(cur)):
                    v = tryInt(cur[i])
                    if v is not None:
                        cur[i] = v
                    else:
                        v = tryFloat(cur[i])
                        if v is not None:
                            cur[i] = v
                    if str(cur[i]) == 'None':
                        cur[i] = ''
                rows.append(cur)
        columns = rows[0]
        rows = rows[1:]
        return Table(columns, rows)

    def toCsv(self, file_name=None):
        """Returns string with CSV representation of current Table.
        If file_name is given, then the data is written into the file."""
        res = ''
        was = False
        for el in self.columns:
            if was:
                res += ','
            else:
                was = True
            res += el
        for row in self.rows:
            res += '\n'
            was = False
            for el in row:
                if was:
                    res += ','
                else:
                    was = True
                res += str(el)

        if file_name:
            with open(file_name, 'w') as f:
                f.write(res)
        return res

    def cell(self, column, row_index=0):
        """Returns cell value by column name or index and a row index (default = 0)."""
        if isinstance(column, str):
            column = self.column_indices[column]
        return self.rows[row_index][column]

    def columnByIndex(self, col_index):
        """Returns new Column object from a column"""
        res = []
        for row in self.rows:
            res.append(row[col_index])
        return Column(res)

    def columnByName(self, col_name):
        """Returns new Column object from a column"""
        return self.columnByIndex(self.column_indices[col_name])

    def renameColumn(self, oldname, newname):
        """Sets new name to a column"""
        if oldname in self.column_indices:
            self.columns[self.column_indices[oldname]] = newname
            self.column_indices[newname] = self.column_indices[oldname]
            self.column_indices.pop(oldname, None)
        else:
            print('Table.renameColumn on incorrect column ' + oldname)

    def apply(self, ind, task):
        """Applies lambda or function to all the column values.
        Ind must be a name or an index of a column.
        Task must be a function or a lambda expression."""
        if isinstance(ind, str):
            ind = self.column_indices[ind]
        elif not isinstance(ind, int):
            raise ValueError('Table.apply first argument must be either int or str!')
        for row in self.rows:
            row[ind] = task(row[ind])

    def groupby(self, keys=None):
        """Returns new Grouped object for current Table.
        Keys must be a list columns names."""
        if keys is None:
            keys = []
        if not iscollection(keys):
            keys = [keys]
        res = Grouped(keys, self.columns, self.column_indices)
        for row in self.rows:
            res.add(row)
        return res

    def pivot(self, newcol, newrow, newval, empty=None):
        """Returns new pivot Table based on current one.
        Newcol is a name of column that will be used for columns.
        Newrow is a name of column that will be used for rows.
        Newval is a name of column that will be used for values.
        Empty will be used for cells without a value."""
        indcol = self.column_indices[newcol]
        indrow = self.column_indices[newrow]
        indval = self.column_indices[newval]
        colsels = []
        rowsels = []
        vals = {}
        for row in self.rows:
            curcol = row[indcol]
            currow = row[indrow]
            curval = row[indval]
            if not curcol in colsels:
                colsels.append(curcol)
            if not currow in rowsels:
                rowsels.append(currow)
            if curcol not in vals:
                vals[curcol] = {}
            vals[curcol][currow] = curval
        colsels = sorted(colsels)
        rowsels = sorted(rowsels)
        rows = []
        for currow in rowsels:
            row = [currow]
            for curcol in colsels:
                if currow in vals[curcol]:
                    row.append(vals[curcol][currow])
                else:
                    row.append(empty)
            rows.append(row)
        return Table([newrow] + colsels, rows)

    @classmethod
    def merge(cls, tl, tr, keys, how='inner', empty=None):
        """Returns new Table as a join of given two.
        TL, TR must be instances of Table class.
        Keys must be a list of columns names.
        How may be one of ['inner', 'left', 'right', 'outer'].
        Empty will be used for cells without a value."""
        doleft = how == 'left' or how == 'outer'
        doright = how == 'right' or how == 'outer'
        if not iscollection(keys):
            keys = [keys]

        rescol = []
        resrow = []

        # Key index to left keys
        key2leftcol = [0] * len(keys)
        for i in range(tl.colcnt):
            for j in range(len(keys)):
                if tl.columns[i] == keys[j]:
                    key2leftcol[j] = i
            rescol.append(tl.columns[i])

        # Right keys to key index
        rightcol2key = []
        for i in range(tr.colcnt):
            tokey = None
            for j in range(len(keys)):
                if tr.columns[i] == keys[j]:
                    tokey = j
                    break
            if tokey is None:
                rescol.append(tr.columns[i])
            rightcol2key.append(tokey)

        # Inner join
        usedrowsleft = [False] * tl.rowcnt
        usedrowsright = [False] * tr.rowcnt

        for i in range(tl.rowcnt):
            rl = tl.rows[i]
            for j in range(tr.rowcnt):
                rr = tr.rows[j]
                match = True
                for el in keys:
                    if rl[tl.column_indices[el]] != rr[tr.column_indices[el]]:
                        match = False
                        break
                if match:
                    usedrowsleft[i] = True
                    usedrowsright[j] = True

                    row = []
                    for el in rl:
                        row.append(el)
                    for k in range(tr.colcnt):
                        if rightcol2key[k] is None:
                            row.append(rr[k])
                    resrow.append(row)

        if doleft:
            for i in range(tl.rowcnt):
                if not usedrowsleft[i]:
                    row = []
                    for el in tl.rows[i]:
                        row.append(el)
                    for k in range(tr.colcnt):
                        if rightcol2key[k] is None:
                            row.append(empty)
                    resrow.append(row)

        if doright:
            for i in range(tr.rowcnt):
                if not usedrowsright[i]:
                    row = []
                    for i in range(tl.colcnt):
                        row.append(empty)
                    rr = tr.rows[i]
                    for k in range(tr.colcnt):
                        if rightcol2key[k] is None:
                            row.append(rr[k])
                        else:
                            row[rightcol2key[k]] = rr[k]
                    resrow.append(row)

        return Table(rescol, resrow)

    def loc(self, prism):
        """Returns new Table as filtered current one by given Column object with boolean values"""
        if not isinstance(prism, Column):
            raise ValueError('Table.loc takes one Column argument')
        la = len(self.rows)
        lb = len(prism)
        if la != lb:
            raise ValueError('Table.loc arguments len must be the same')
        res = []
        for i in range(la):
            if prism[i]:
                res.append(self.rows[i])
        return Table(self.columns[:], res)

    def sort(self, cols, asc=True):
        """Sorts rows in place"""
        if not iscollection(cols):
            cols = [cols]
        l = len(cols)
        for i in range(l):
            ind = cols[l - 1 - i]
            if isinstance(ind, str):
                ind = self.column_indices[ind]
            if iscollection(asc):
                order = asc[l - 1 - i]
            else:
                order = asc
            self.rows = sorted(self.rows, key=lambda x: x[ind], reverse=not order)

    def copy(self):
        """Returns new Table as a deep copy of this one"""
        cols = self.columns[:]
        rows = []
        for row in self.rows:
            rows.append(row[:])
        return Table(cols, rows)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.columnByIndex(index)
        elif isinstance(index, str):
            return self.columnByName(index)
        else:
            raise ValueError('Table.__getitem__ argument must be either int or str!')

    minshowrows = 3
    maxshowrows = 6
    minshowcols = 6
    maxshowcols = 8

    def __need_cut__(self):
        """Returns if should show all the rows and columns."""
        showrowscnt = Table.minshowrows
        showcolscnt = Table.minshowcols
        hiddenrows = True
        hiddencols = True
        if self.rowcnt <= Table.maxshowrows:
            showrowscnt = self.rowcnt
            hiddenrows = False
        if self.colcnt <= Table.maxshowcols:
            showcolscnt = self.colcnt
            hiddencols = False
        return showrowscnt, showcolscnt, hiddenrows, hiddencols

    def __str__(self):
        showrowscnt, showcolscnt, hiddenrows, hiddencols = self.__need_cut__()
        res = '- Table object, ' + str(len(self.columns)) + ' columns, ' + str(len(self.rows)) + ' rows.\n'
        res += ' '.join(map(lambda x: repr(x), self.columns[:showcolscnt]))
        if hiddencols:
            res += ' ...'
        for row in self.rows[:showrowscnt]:
            res += '\n' + ' '.join(map(lambda x: repr(x), row[:showcolscnt]))
        if hiddenrows:
            res += '\n. . .'
        return res

    def html(self):
        showrowscnt, showcolscnt, hiddenrows, hiddencols = self.__need_cut__()
        res = '<table><tr><th>'
        res += '</th><th>'.join(map(lambda x: repr(x), self.columns[:showcolscnt]))
        if hiddencols:
                res += '</th><th>...'
        res += '</th></tr>'
        for row in self.rows[:showrowscnt]:
            res += '<tr><td>'
            res += '</td><td>'.join(map(lambda x: repr(x), row[:showcolscnt]))
            if hiddencols:
                res += '</td><td>...'
            res += '</td></tr>'
        if hiddenrows:
            res += '<tr><th>'
            res += '</th><th>'.join(map(lambda x: str(x), ['...'] * showcolscnt))
            if hiddencols:
                    res += '</th><th>...'
            res += '</th></tr>'
        res += '<table>'
        return res

    def _repr_html_(self):
        res = '<b>Table</b> object, ' + str(len(self.columns)) + ' columns, ' + str(len(self.rows)) + ' rows.<br>'
        res += self.html()
        return res

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        """Returns number of rows"""
        return len(self.rows)
