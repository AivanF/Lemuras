__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'projects@aivanf.com'
__version__ = '1.1.8'
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

from datetime import date, datetime
import numbers
import re
import csv
import json
import sys

if sys.version_info[0] == 2:
	from io import BytesIO
	file_container = lambda x: BytesIO(bytes(x))

else:
	from io import StringIO
	file_container = lambda x: StringIO(x)

try:
	from bs4 import BeautifulSoup
except ImportError:
	BeautifulSoup = None


def iscollection(x):
	return isinstance(x, list) or isinstance(x, tuple) or isinstance(x, set)


# LAmbda LEngth POsitive
lalepo = lambda x: len(x) > 0


def makeStr(x, default=None):
	if isinstance(x, str):
		return x
	elif default is None:
		return str(x)
	else:
		return default


def tryInt(x, default=0):
	try:
		return int(x)
	except:
		return default


def tryFloat(x, default=0):
	try:
		return float(x)
	except:
		return default


def tryDatetime(x, default=None):
	if isinstance(x, datetime):
		return x
	try:
		return datetime.strptime(x[:19], '%Y-%m-%d %H:%M:%S')
	except:
		pass
	try:
		return datetime.strptime(x[:16], '%Y-%m-%d %H:%M')
	except:
		pass
	return default


def tryDate(x, default=None):
	if isinstance(x, date):
		return x
	try:
		return datetime.strptime(x[:10], '%Y-%m-%d').date()
	except:
		pass
	try:
		return datetime.strptime(x[:10], '%m/%d/%Y').date()
	except:
		pass
	try:
		return datetime.strptime(x[:10], '%d.%m.%Y').date()
	except:
		pass
	return default


def parse_value(val, empty=''):
	v = tryInt(val, None)
	if v is not None:
		return v
	else:
		v = tryFloat(val, None)
		if v is not None:
			return v
		else:
			v = tryDatetime(val, None)
			if v is not None:
				return v
			else:
				v = tryDate(val, None)
				if v is not None:
					return v
	v = str(val).lower()
	if v == 'none' or v == 'null' or len(str(v)) == 0:
		return empty
	return val


typefuns = {
	'str': makeStr,
	'int': tryInt,
	'float': tryFloat,
	'date': tryDate,
	'datetime': tryDatetime,
}


def parse_row(lst, empty=''):
	"""Takes a list of strings and returns list of values with different types."""
	for i in range(len(lst)):
		lst[i] = parse_value(lst[i])
	return lst


def repr_cell(x):
	if isinstance(x, date):
		return str(x)
	else:
		return repr(x)


def jsonable(o):
	return isinstance(o, str) or isinstance(o, int) or isinstance(o, float) or isinstance(o, list) or isinstance(o, tuple) or isinstance(o, dict)


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
	if len(lst) > 0:
		return 1.0 * sum(lst) / len(lst)
	else:
		return 0


def std(lst, ddof=0):
	"""Calculates the population standard deviation by default;
	specify ddof=1 to compute the sample standard deviation."""
	if len(lst) >= 1+ddof:
		c = avg(lst)
		# Sum of square deviations
		ss = sum((x-c)**2 for x in lst)
		# Dispersion
		disp = ss / (len(lst) - ddof)
		return disp ** 0.5
	else:
		return 0


def numbers_only(lst):
	return [x for x in lst if isinstance(x, numbers.Number)]


def call_with_numbers_only(task):
	"""Returns a function whuch takes a list and executes
	argument function with numbers from that list.
	"""
	def inner(lst):
		return task(numbers_only(lst))
	return inner


aggfuns = {
	'avg': call_with_numbers_only(avg),
	'mean': call_with_numbers_only(avg),
	'mode': call_with_numbers_only(mode),
	'middle': call_with_numbers_only(median),
	'median': call_with_numbers_only(median),
	'std': call_with_numbers_only(std),
	'sum': call_with_numbers_only(sum),
	'min': call_with_numbers_only(min),
	'max': call_with_numbers_only(max),
	'count': len,
	'first': lambda x: x[0] if len(x) > 0 else None,
	'last': lambda x: x[-1] if len(x) > 0 else None,
}


class Column(object):
	def __init__(self, values, title='-'):
		self.values = values
		self.title = title
		self.idx = 0

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self.values[self.idx-1]
		except IndexError:
			self.idx = 0
			raise StopIteration
	
	# Python 2.x compatibility
	next = __next__

	@classmethod
	def make(cls, size, values=None, title='-'):
		return Column([values] * size, title)

	def get_type(self):
		"""Returns column type and max symbols length."""
		# None Int Float String Mixed
		tp = 'n'
		# varchar length
		ln = 0

		cnt = len(self.values)
		if cnt > 4096:
			cnt = int(cnt / 3)
		elif cnt > 2048:
			cnt = int(cnt / 2)

		for el in self.values[:cnt]:
			ln = max(ln, len(str(el)))

			if isinstance(el, int):
				kind = 'i'
			elif isinstance(el, float):
				kind = 'f'
			elif isinstance(el, datetime):
				kind = 't'
			elif isinstance(el, date):
				kind = 'd'
			else:
				kind = 's'

			if tp == 'n':
				tp = kind
			elif tp != kind:
				if tp == 'f' and kind == 'i':
					pass
				elif tp == 'i' and kind == 'f':
					tp = 'f'
				else:
					tp = 'm'

		return tp, ln

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
		"""Returns new Column object with applied len to str of current values."""
		res = []
		for el in self.values:
			res.append(len(str(el)))
		return Column(res)

	def count(self):
		"""Returns count of true values."""
		res = 0
		for el in self.values:
			if el:
				res += 1
		return res

	def value_counts(self):
		"""Returns number of each value."""
		# TODO: here!
		return None

	def nunique(self):
		"""Returns number of unique values."""
		return len(set(self.values))

	def none_to(self, default=0):
		"""Replaces None elements with a given value."""
		for i in range(len(self.values)):
			if self.values[i] is None:
				self.values[i] = default
		return self

	def apply(self, task, *args):
		""" Several cases are possible:
		1. Applies function for each column value if a function is given.
		2. Changes elements types if type name is given.
		The following are supported: str, int, float, date, datetime.
		All the types can take a default value.
		3. Returns an aggregated value.
		"""
		# TODO: make same behaviour in Table.apply
		if isinstance(task, str):
			if task in aggfuns:
				return aggfuns[task](self.values, *args)
			elif task in typefuns:
				task = typefuns[task]
				# Continue function applying
			else:
				raise ValueError('Applied function named "{}" does not exist!'.format(task))
	
		"""Returns this column with applied lambda or function to all the values.
		The argument must be a function or a lambda expression."""
		res = []
		for i in range(len(self.values)):
			self.values[i] = task(self.values[i], *args)
			# res.append(task(self.values[i]))
		return self
		# return Column(res)

	def copy(self):
		"""Returns new Column as a deep copy of this one"""
		return Column(values=self.values[:], title=self.title)

	def _repr_html_(self):
		n = len(self.values)
		ns = False
		if n > 12:
			n = 10
			ns = True
		res = '<b>Column</b> object, title: "{}" values: {}.'.format(self.title, self.values[:n])
		if ns:
			res += ' . .'
		return res

	def __repr__(self):
		n = len(self.values)
		ns = False
		if n > 12:
			n = 10
			ns = True
		res = '- Column object, title: "{}" values: {}.'.format(self.title, self.values[:n])
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

# END class Column


class Grouped(object):
	def __init__(self, keys, columns, column_indices):
		self.keys = keys
		self.count = len(keys)
		# {'target_column_name': {'new_column_name': function}}
		self.fun = None

		# Indices of key columns in original table
		self.gun = []
		for el in keys:
			self.gun.append(column_indices[el])

		# Columns names of grouped rows
		self.columns = {}
		# Whether old columns should be saved
		self.column_indices = []
		step = 0
		for cur in columns:
			if cur not in keys:
				self.column_indices.append(True)
				self.columns[cur] = step
				step += 1
			else:
				self.column_indices.append(False)

		# Dict of dict of ... of list with a list of columns
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
					# add one more dict layer
					vals[cur] = {}
			vals = vals[cur]

		# Save values with appropriate indices only - not key columns
		step = 0
		for i in range(len(self.columns)):
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
		"""Recursive method to move through grouping keys.
		Task takes list of keys values and list of columns."""
		res = []
		if isinstance(vals, dict):
			for key in vals:
				res.extend(self.__recurs__(vals[key], keys + [key], task))
		elif iscollection(vals):
			v = task(keys, vals)
			if v is not None:
				res.append(v)
		return res

	def agg(self, fun, default_fun=None):
		"""Returns new Table object from aggregated groups.
		The argument must be a dictionary which keys are old columns names,
		and the values are other dictionaries where keys are new columns names,
		and the values are strings with aggregation functions names or function or lambdas.
		The last argument allows to aggregate all the rows with single or multiple functions.
		"""

		if default_fun is not None:
			for target_name in self.columns:
				if target_name not in fun:
					fun[target_name] = {}
				if isinstance(default_fun, dict):
					for key in default_fun:
						fun[target_name]['{}_{}'.format(target_name, key)] = default_fun[key]
				else:
					fun[target_name][target_name] = default_fun

		self.fun = fun
		cols = self.keys
		for target_name in fun:
			for new_name in fun[target_name]:
				cols.append(new_name)
		rows = self.__recurs__(self.values, [], self.__agglist__)
		return Table(cols, rows, 'Aggregated')

	def __make_group__(self, keys, cols, should_add_keys):
		t = 'Group '
		for i in range(len(self.keys)):
			t += '{}={} '.format(self.keys[i], keys[i])
		res = Table([], [], t[:-1])
		if should_add_keys:
			for i in range(len(self.keys)):
				res[self.keys[i]] = [keys[i]] * len(cols[0])
		for el in self.columns:
			res[el] = cols[self.columns[el]]
		return res

	def split(self, should_add_keys=True):
		"""Returns a list with new Table objects - different groups."""
		return self.__recurs__(self.values, [], lambda keys, cols: self.__make_group__(keys, cols, should_add_keys))

	def get_group(self, search_keys, should_add_keys=True):
		"""Returns None or new Table objects as a group with specified keys."""
		if not iscollection(search_keys):
			search_keys = [search_keys]
		def findTable(keys, cols):
			well = True
			for i in range(len(keys)):
				if keys[i] != search_keys[i]:
					well = False
					break
			if well:
				return self.__make_group__(keys, cols, should_add_keys)
		res = self.__recurs__(self.values, [], findTable)
		if len(res) > 0:
			return res[0]
		else:
			return None

	def counts(self):
		"""Returns new Table object with counts of the groups."""
		rows = []
		todo = lambda x, y: rows.append(x + [len(y[0])])
		self.__recurs__(self.values, [], todo)
		return Table(self.keys + ['counts'], rows, 'Groups')

	def _repr_html_(self):
		res = '<b>Grouped</b> object, keys: {}, old columns: {}.<br>\n'.format(
			self.keys, list(self.columns.keys())
		)
		res += self.counts().html()
		return res

	def __repr__(self):
		return '- Grouped object, keys: {}, old columns: {}.'.format(
			self.keys, list(self.columns.keys())
		)

# END class Grouped


class Table(object):
	def __init__(self, columns, rows, title=None):
		self.columns = columns
		self.rows = rows
		if title is None:
			title = 'NoTitle'
		self.title = title
		self.column_indices = {}
		self.types = None
		for i in range(len(self.columns)):
			self.column_indices[self.columns[i]] = i
		self.idx = 0

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self.rows[self.idx-1]
		except IndexError:
			self.idx = 0
			raise StopIteration
	
	# Python 2.x compatibility
	next = __next__

	@property
	def colcnt(self):
		return len(self.columns)

	@property
	def rowcnt(self):
		return len(self.rows)

	def cell(self, column, row_index=0):
		"""Returns cell value by column name or index and a row index (default = 0)."""
		if isinstance(column, str):
			column = self.column_indices[column]
		return self.rows[row_index][column]

	def set_cell(self, column, row_index, value):
		"""Sets cell value by column name or index and a row index (default = 0)."""
		if isinstance(column, str):
			column = self.column_indices[column]
		self.rows[row_index][column] = value

	def column(self, column):
		"""Returns new Column object. Argument must be a column name or index.
		This allocates new memory for each cell, you should not use it twice for the same column."""

		if isinstance(column, str):
			column = self.column_indices[column]
		res = []
		for row in self.rows:
			res.append(row[column])
		return Column(res, self.columns[column])

	def set_column(self, column, data):
		"""Sets values for existing column. First argument must be a column name or index.
		Second argument must be either a list or a Column object."""

		if isinstance(column, str):
			name = column
			ind = self.column_indices[column]
		else:
			name = self.columns[column]
			ind = column

		if isinstance(data, Column):
			pass
		elif iscollection(data):
			data = Column(data)
		else:
			raise ValueError('Table.set_column first argument must be either list or Column object!')

		if len(data) != self.rowcnt:
			raise ValueError('Table.set_column column length must be equal to table rows count!')
		for i in range(self.rowcnt):
			self.rows[i][ind] = data[i]

	def add_column(self, data, title=None):
		"""Adds new column. First argument must be either a list or a Column object.
		Second argument is optional title."""

		if isinstance(data, Column):
			if title is None:
				title = data.title
		elif iscollection(data):
			if title is None:
				title = 'NoTitle'
			data = Column(data)
		else:
			raise ValueError('Table.add_column first argument must be either list or Column object!')

		if self.rowcnt == 0 and self.colcnt == 0:
			self.column_indices[title] = self.colcnt
			self.columns.append(title)
			for i in range(len(data)):
				self.rows.append([data[i]])
		else:
			if len(data) != self.rowcnt:
				raise ValueError('Table.add_column column length must be equal to table rows count!')
			self.column_indices[title] = self.colcnt
			self.columns.append(title)
			for i in range(self.rowcnt):
				self.rows[i].append(data[i])

	def delete_column(self, column):
		"""Deletes column. Argument must be a column name or index."""
		if isinstance(column, str):
			name = column
			ind = self.column_indices[column]
		else:
			name = self.columns[column]
			ind = column
		del self.columns[ind]
		for row in self.rows:
			del row[ind]
		self.column_indices.pop(name, None)

	def __getitem__(self, column):
		return self.column(column)

	def __setitem__(self, column, data):
		if column in self.columns:
			self.set_column(column, data)
		else:
			self.add_column(data, column)

	def row(self, row_index=0):
		"""Returns a list with row values."""
		return self.rows[row_index][:]

	def row_named(self, row_index=0):
		"""Returns a dictionary with row values."""
		res = {}
		for i in range(self.colcnt):
			res[self.columns[i]] = self.rows[row_index][i]
		return res

	def add_row(self, data, strict=True, empty=None, preprocess=False):
		"""Adds a row to the Table. The argument must be either list or dictionary."""
		if iscollection(data):
			if len(data) != self.colcnt:
				raise ValueError('Table.add_row list argument must have length equal to columns count!')
			row = []
			for el in data:
				if preprocess:
					row.append(parse_value(el))
				else:
					row.append(el)
			self.rows.append(row)
		elif isinstance(data, dict):
			row = []
			for el in self.columns:
				if el not in data:
					if strict:
						raise ValueError('Table.add_row dict argument does not have key ' + el + '!')
					else:
						row.append(empty)
				else:
					if preprocess:
						row.append(parse_value(data[el]))
					else:
						row.append(data[el])
			self.rows.append(row)
		else:
			raise ValueError('Table.add_row argument must be either list or dict!')

	def delete_row(self, row_index=0):
		del self.rows[row_index]

	def find_types(self):
		rows = []
		for el in self.columns:
			tp, ln = self[el].get_type()
			rows.append((el, tp, ln))
		self.types = Table(['Column', 'Type', 'Symbols'], rows, 'Types')
		return self.types

	def append(self, other):
		"""Adds rows from other Table object.
		The other table must have at least the same columns."""
		for i in range(other.rowcnt):
			self.add_row(other.row_named(i))

	@classmethod
	def concat(cls, tables):
		"""Returns new Table object with data from list of Table objects.
		Columns are the same as in the first table.
		Other table must have at least the same columns."""

		res = tables[0].copy()
		for el in tables[1:]:
			for i in range(el.rowcnt):
				res.add_row(el.row_named(i))
			# It's faster, but less powerful
			# for row in el.rows:
			#     res.add_row(row)
		res.title = "Concat"
		return res

	def rename(self, oldname, newname):
		"""Sets new name to a column."""
		if oldname in self.column_indices:
			if oldname != newname:
				self.columns[self.column_indices[oldname]] = newname
				self.column_indices[newname] = self.column_indices[oldname]
				self.column_indices.pop(oldname, None)
		else:
			print('Table.rename on incorrect column {}'.format(oldname))

	def apply(self, ind, task):
		"""Applies lambda or function to all the column values.
		First argument must be a name or an index of a column.
		Second argument must be a function or a lambda expression."""

		if isinstance(ind, str):
			ind = self.column_indices[ind]
		elif not isinstance(ind, int):
			raise ValueError('Table.apply first argument must be either int or str!')
		for row in self.rows:
			row[ind] = task(row[ind])

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
		return Table(self.columns[:], res, 'Filtered {}'.format(self.title))

	def sort(self, cols, asc=True):
		"""Sorts rows in place.
		First argument must be a column name or a list of them.
		Second argument may be a boolean or a list of them."""

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
		return Table(cols, rows, self.title)

	def groupby(self, keys=None):
		"""Returns new Grouped object for current Table.
		Keys must be a list with columns names."""

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
		# Dictionary with columns->rows->values
		vals = {}

		# Fill the dictionary
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

		# Create plain rows
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
		return Table([newrow] + colsels, rows, 'Pivot of {}'.format(self.title))

	@classmethod
	def merge(cls, tl, tr, keys, how='inner', empty=None):
		"""Returns new Table as a join of given two.
		TL, TR must be instances of Table class.
		Keys must be a list of columns names.
		How may be one of ['inner', 'left', 'right', 'outer'].
		Empty will be used for cells without a value."""

		doleft = (how == 'left') or (how == 'outer')
		doright = (how == 'right') or (how == 'outer')
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

		# If rows are used in inner join
		usedrowsleft = [False] * tl.rowcnt
		usedrowsright = [False] * tr.rowcnt

		for i in range(tl.rowcnt):
			rl = tl.rows[i]
			for j in range(tr.rowcnt):
				rr = tr.rows[j]
				match = True
				# Check all keys are the same
				for el in keys:
					if rl[tl.column_indices[el]] != rr[tr.column_indices[el]]:
						match = False
						break

				if match:
					# Mark the matched rows
					# so they won't be used in left / right / outer
					usedrowsleft[i] = True
					usedrowsright[j] = True

					row = []
					# Add all the left side
					for el in rl:
						row.append(el)
					# Add right side if not keys
					# they are already in left side
					for k in range(tr.colcnt):
						if rightcol2key[k] is None:
							row.append(rr[k])
					resrow.append(row)

		if doleft:
			for i in range(tl.rowcnt):
				# Add the row if it wasn't used in inner
				if not usedrowsleft[i]:
					row = []
					# Fill left side with values
					for el in tl.rows[i]:
						row.append(el)
					# Fill right side with empty
					for k in range(tr.colcnt):
						# Key are already in the left side
						if rightcol2key[k] is None:
							# If not a key, just add the value
							row.append(empty)
					resrow.append(row)

		if doright:
			for i in range(tr.rowcnt):
				# Add the row if it wasn't used in inner
				if not usedrowsright[i]:
					row = []
					# Fill left side with empty
					for i in range(tl.colcnt):
						row.append(empty)
					rr = tr.rows[i]
					# Fill right side with values
					for k in range(tr.colcnt):
						if rightcol2key[k] is None:
							# If not a key, just add the value
							row.append(rr[k])
						else:
							# If a key, put it in the left side
							row[rightcol2key[k]] = rr[k]
					resrow.append(row)

		title = 'Merged {} {} & {}'.format(how, tl.title, tr.title)
		return Table(rescol, resrow, title)

	def nunique(self):
		"""Returns new Table object with counts of unique values in columns of this Table."""
		rows = []
		for el in self.columns:
			col = self.column(el)
			cnt = col.nunique()
			rows.append([ el, cnt ])
		# title = 'Unique values in ' + self.title
		title = 'Unique values'
		return Table(['Column', 'Counts'], rows, title)

	@classmethod
	def from_csv(cls, data, inline=True, empty=None, preprocess=True, title=None, delimiter=',', quotechar='"'):
		"""Returns new Table object from CSV data.
		If inline is True (default), then the first argument is considered
		as a string with CSV data itself. Otherwise, the first argument
		is considered as a filename where the CSV data is located."""

		if delimiter is None:
			if not inline and '.tsv' in data:
				delimiter = '\t'
			else:
				delimiter = ','

		columns = []
		rows = []
		if inline:
			f = file_container(data)
			if title is None:
				title = 'from CSV'
		else:
			f = open(data, 'r+', encoding='utf-8')
			if title is None:
				title = data.split('/')[-1]
		with f:
			csvreader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
			is_first = True
			for row in csvreader:
				if is_first:
					is_first = False
					columns = row[:]
				else:
					if preprocess:
						row = parse_row(row, empty=empty)
					rows.append(row)
		return Table(columns, rows, title)

	def to_csv(self, file_name=None, delimiter=',', quotechar='"'):
		"""Returns string with CSV representation of current Table.
		If file_name is given, then the data is also written into the file."""
		res = ''
		with file_container('') as temp:
			writer = csv.writer(temp, delimiter=delimiter, quotechar=quotechar)
			writer.writerow(self.columns)
			for row in self.rows:
				writer.writerow(row)
			temp.seek(0)
			res = temp.read()

		if file_name is not None:
			with open(file_name, 'w', encoding='utf-8') as f:
				f.write(res)
		return res

	def to_sql_create(self):
		def sql_type(tp, ln):
			if tp == 'i':
				if ln < 4:
					return 'int(1)'
				elif ln < 6:
					return 'int(2)'
				elif ln < 9:
					return 'int(3)'
				elif ln < 11:
					return 'int(4)'
				else:
					return 'int(8)'
			if tp == 'f':
				return 'float'
			if tp == 'd':
				return 'date'
			if tp == 't':
				return 'datetime'
			return 'varchar(' + str(ln) + ')'

		self.find_types()
		res = 'CREATE TABLE `{}` ('.format(self.title)
		firstrow = True
		for row in self.types.rows:
			if firstrow:
				firstrow = False
				res += '\n'
			else:
				res += ',\n'
			res += '  `' + row[0] + '` ' + sql_type(row[1], row[2])
		res += '\n) ;'
		return res

	def to_sql_values(self):
		if self.types is None:
			self.find_types()
		if self.rowcnt < 1:
			return ''
		res = 'INSERT INTO `{}` VALUES '.format(self.title)
		firstrow = True
		for row in self.rows:
			if firstrow:
				firstrow = False
			else:
				res += ', '
			firstcell = True
			res += "("
			for i in range(self.colcnt):
				if firstcell:
					firstcell = False
				else:
					res += ","
				ctp = self.types.cell(1, i)
				if ctp == 's' or ctp == 'm' or ctp == 'd' or ctp == 't':
					res += "'" + str(row[i]) + "'"
				else:
					res += str(row[i])
			res += ")"
		res += ';'
		return res

	@classmethod
	def from_sql_create(cls, data):
		data = data.replace('\n', ' ')
		title = list(filter(lalepo, data.split('(')[0].split(' ')))[-1]
		title = title.replace('`', '')
		cols = []
		b = data.find('(') + 1
		tps = data[b:].split(',')
		for el in tps:
			ch = el.lower()
			if (' int' in ch) or (' float' in ch) or (' date' in ch) or (' text' in ch) or ('char(' in ch):
				# print("- Column is here!")
				# print(ch)
				cols.append(list(filter(lalepo, el.split(' ')))[0].replace('`', ''))
		return Table(cols, [], title)

	@classmethod
	def from_sql_result(cls, data, empty=None, preprocess=True, title='from SQL res'):
		if data[0] == '+':
			data = data[data.find('\n') + 1:]
		cols = data[:data.find('\n')]
		cols = cols.split('|')[1:-1]
		cols = list(map(lambda x: x.strip(), cols))
		data = data[data.find('\n') + 1:]
		data = data.split('\n')[1:-1]
		rows = []
		for ln in data:
			cur = ln.split('|')[1:-1]
			cur = list(map(lambda x: x.strip(), cur))
			if preprocess:
					cur = parse_row(cur, empty=empty)
			rows.append(cur)
		return Table(cols, rows, title)

	def add_sql_values(self, data, empty=None):
		p = re.compile("(\d+|\'.*?\')\s*,?")
		def cutstr(x):
			if len(x) > 1:
				if x[0] == "'" and x[-1] == "'":
					return x[1:-1]
			return x
		while True:
			b = data.find('(') + 1
			e = data.find(')')
			if b > 0 and e > b:
				# cur = data[b:e].replace("'", '').split(',')
				cur = p.findall(data[b:e])
				cur = list(map(cutstr, cur))
				cur = parse_row(cur, empty=empty)
				self.add_row(cur, preprocess=True)
				data = data[e+1:]
				continue
			else:
				break

	@classmethod
	def from_json(cls, data, preprocess=True, title='from JSON'):
		data = json.loads(data)
		res = Table(data['columns'], [], title)
		for row in data['rows']:
			res.add_row(row, preprocess=preprocess)
		if 'title' in data:
			res.title = data['title']
		else:
			res.title = title
		return res

	def to_json(self, as_dict=False, pretty=False):
		body = []
		if as_dict:
			for el in self.rows:
				d = {}
				for i in range(len(self.columns)):
					if jsonable(el[i]):
						d[self.columns[i]] = el[i]
					else:
						d[self.columns[i]] = str(el[i])
				body.append(d)
		else:
			for el in self.rows:
				cur = []
				for o in el:
					if jsonable(o):
						cur.append(o)
					else:
						cur.append(str(o))
				body.append(cur)
		res = { 'columns': self.columns, 'rows': body, 'title': self.title }
		if pretty:
			res = json.dumps(res, indent=2, separators=(', ',': '))
			res = res.replace(', \n      ', ', ')
			res = res.replace(', \n    ', ', ')
			res = res.replace('], \n    [', '], [')
			res = res.replace('}, \n    {', '}, {')
		else:
			res = json.dumps(res, separators=(',',':'))
		return res

	@classmethod
	def from_html(cls, data, title='from HTML'):
		if BeautifulSoup is None:
			raise ImportError('BeautifulSoup4 is needed for HTML parsing!')
		# Parse HTML
		data = BeautifulSoup(data, 'lxml')
		# Find table
		data = data.find_all('table')[0]
		# Iterate over rows
		columns = None
		rows = []
		for row in data.find_all('tr'):
			# Iterate over values
			values = []
			for column in row.find_all('td'):
				values.append(column.get_text())
			if len(values) == 0:
				for column in row.find_all('th'):
					values.append(column.get_text())
			if columns is not None:
				rows.append(parse_row(values))
			else:
				columns = values
		return Table(columns, rows, title)

	minshowrows = 4
	maxshowrows = 7
	minshowcols = 6
	maxshowcols = 8

	def __need_cut__(self, cut=True):
		"""Returns if should show all the rows and columns."""
		showrowscnt = Table.minshowrows
		showcolscnt = Table.minshowcols
		hiddenrows = True
		hiddencols = True
		if not cut or self.rowcnt <= Table.maxshowrows:
			showrowscnt = self.rowcnt
			hiddenrows = False
		if not cut or self.colcnt <= Table.maxshowcols:
			showcolscnt = self.colcnt
			hiddencols = False
		return showrowscnt, showcolscnt, hiddenrows, hiddencols

	def __str__(self):
		showrowscnt, showcolscnt, hiddenrows, hiddencols = self.__need_cut__()
		res = '- Table object, title: "{}", {} columns, {} rows.\n'.format(self.title, len(self.columns), len(self.rows))
		res += ' '.join(map(lambda x: repr(x), self.columns[:showcolscnt]))
		if hiddencols:
			res += ' ...'
		for row in self.rows[:showrowscnt]:
			res += '\n' + ' '.join(map(lambda x: repr_cell(x), row[:showcolscnt]))
		if hiddenrows:
			res += '\n. . .'
		return res

	def html(self, cut=True):
		showrowscnt, showcolscnt, hiddenrows, hiddencols = self.__need_cut__(cut)
		res = '<table>\n<tr><th>'
		res += '</th><th>'.join(map(lambda x: repr(x), self.columns[:showcolscnt]))
		if hiddencols:
			res += '</th><th>...'
		res += '</th></tr>\n'
		for row in self.rows[:showrowscnt]:
			res += '<tr><td>'
			res += '</td><td>'.join(map(lambda x: repr_cell(x), row[:showcolscnt]))
			if hiddencols:
				res += '</td><td>...'
			res += '</td></tr>\n'
		if hiddenrows:
			res += '<tr><th>'
			res += '</th><th>'.join(map(lambda x: str(x), ['...'] * showcolscnt))
			if hiddencols:
					res += '</th><th>...'
			res += '</th></tr>'
		res += '</table>'
		return res

	def _repr_html_(self):
		res = '<b>Table</b> object, title: <b>{}</b>, {} columns, {} rows.<br>\n'.format(self.title, len(self.columns), len(self.rows))
		res += self.html()
		return res

	def __repr__(self):
		return self.__str__()

	def __len__(self):
		"""Returns number of cells - product of number of rows and columns."""
		return self.rowcnt * self.colcnt

# END class Table
