__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'projects@aivanf.com'
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

import datetime
import re
import csv
import json
from .utils import main_str, file_container, BeautifulSoup, iscollection, jsonable, lalepo
from .processing import parse_value, parse_row, aggfuns, typefuns, applyfuns
from .column import Column


def repr_cell(x, quote_strings=False):
	if isinstance(x, datetime.date):
		return str(x)
	if not quote_strings and isinstance(x, main_str):
		return x
	return repr(x)


class Row(object):
	def __init__(self, table, row_index):
		self.table = table
		self.row_index = row_index
		self.idx = 0

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self[self.idx-1]
		except IndexError:
			self.idx = 0
			raise StopIteration
	
	# Python 2.x compatibility
	next = __next__

	@property
	def colcnt(self):
		return self.table.colcnt

	@property
	def columns(self):
		return self.table.columns

	def __getitem__(self, column):
		return self.table.cell(column, self.row_index)

	def __setitem__(self, column, value):
		self.table.set_cell(column, self.row_index, value)

	def _repr_html_(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.table.rows[self.row_index])
		res = '<b>Row</b> {} of table <b>{}</b><br>\n[{}]'.format(self.row_index, self.table.title, ','.join(values))
		res += self.html()
		return res

	def __len__(self):
		"""Returns number of columns."""
		return self.table.colcnt

	def __str__(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.table.rows[self.row_index])
		return '- Row {} of table "{}"\n[{}]'.format(self.row_index, self.table.title, ','.join(values))

	def __repr__(self):
		return self.__str__()


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
			# return self.rows[self.idx-1]
			return self.row(self.idx-1)
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
		# Deep copy:
		# return Column([row[column] for row in self.rows], self.columns[column])
		# Proxy object:
		return Column(values=None, title=self.columns[column], table=self, source_name=self.columns[column])

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

	@classmethod
	def from_columns(cls, columns, title='From columns'):
		res = Table([], [], title)
		for col in columns:
			res.add_column(col)
		return res

	def row(self, row_index=0):
		"""Returns a Row object."""
		if isinstance(row_index, int) and row_index < self.rowcnt and row_index >= -self.rowcnt:
			return Row(self, row_index)
		else:
			raise IndexError('Bad row index!')

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

	def apply(self, ind, task, *args, **kwargs):
		# For compatibility with old versions
		return self[ind].apply(task, *args, **kwargs)

	def calc(self, task, *args, **kwargs):
		res = []
		row = Row(self, 0)
		for i in range(self.rowcnt):
			row.row_index = i
			res.append(task(row, *args, **kwargs))
		return Column(res, 'Calc')

	def loc(self, prism, separate=False):
		"""Returns new Table as filtered current one by given Column object with boolean values"""
		if not isinstance(prism, Column):
			raise ValueError('Table.loc takes one Column argument')
		if len(self.rows) != len(prism):
			raise ValueError('Table.loc argument len must be the same')
		res = []
		for i, checker in enumerate(prism):
			if checker:
				if separate:
					res.append(self.rows[i][:])
				else:
					res.append(self.rows[i])
		title = 'Filtered {}'.format(self.title)
		if separate:
			title += ' Copy'
			columns = self.columns[:]
		else:
			columns = self.columns
		return Table(columns, res, title)

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
		from .grouped import Grouped
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

		for row_index in range(tl.rowcnt):
			rl = tl.rows[row_index]
			for r2_index in range(tr.rowcnt):
				rr = tr.rows[r2_index]
				match = True
				# Check all keys are the same
				for el in keys:
					if rl[tl.column_indices[el]] != rr[tr.column_indices[el]]:
						match = False
						break

				if match:
					# Mark the matched rows
					# so they won't be used in left / right / outer
					usedrowsleft[row_index] = True
					usedrowsright[r2_index] = True

					row = []
					# Add all the left side
					for el in rl:
						row.append(el)
					# Add right side if not keys
					# they are already in left side
					for column_index in range(tr.colcnt):
						if rightcol2key[column_index] is None:
							row.append(rr[column_index])
					resrow.append(row)

		if doleft:
			for row_index in range(tl.rowcnt):
				# Add the row if it wasn't used in inner
				if not usedrowsleft[row_index]:
					row = []
					# Fill left side with values
					for el in tl.rows[row_index]:
						row.append(el)
					# Fill right side with empty
					for column_index in range(tr.colcnt):
						# Key are already in the left side
						if rightcol2key[column_index] is None:
							# If not a key, just add the value
							row.append(empty)
					resrow.append(row)

		if doright:
			for row_index in range(tr.rowcnt):
				# Add the row if it wasn't used in inner
				if not usedrowsright[row_index]:
					row = []
					# Fill left side with empty
					for column_index in range(tl.colcnt):
						row.append(empty)
					rr = tr.rows[row_index]
					# Fill right side with values
					for column_index in range(tr.colcnt):
						if rightcol2key[column_index] is None:
							# If not a key, just add the value
							row.append(rr[column_index])
						else:
							# If a key, put it in the left side
							row[rightcol2key[column_index]] = rr[column_index]
					resrow.append(row)

		title = 'Merged {} {} & {}'.format(how, tl.title, tr.title)
		return Table(rescol, resrow, title)

	def __getattr__(self, attr):
		if attr in aggfuns:
			# Returns new Table object with applied aggregation function to all the columnss
			def inner(*args, **kwargs):
				rows = []
				for col in self.columns:
					val = self[col].calc(attr, *args, **kwargs) 
					rows.append([ col, val ])
				title = '{}.{}()'.format(self.title, attr)
				return Table(['Column', attr], rows, title)
			return inner
		elif attr in applyfuns:
			# Returns new Table object with applied function to all the values
			def inner(*args, **kwargs):
				title = '{}.{}()'.format(self.title, attr)
				# if separate:
				columns = [self[col].apply(attr, separate=True, *args, **kwargs) for col in self.columns]
				return Table.from_columns(columns, title=title)
				# else:
				# 	for col in self.columns:
				# 		self[col].apply(attr, *args, **kwargs) 
				# 	self.title = title
				# 	return self
			return inner
		elif attr in typefuns:
			# Changes types of all the table values
			def inner(*args, **kwargs):
				for col in self.columns:
					self[col].apply(attr)
			return inner
		else:
			raise AttributeError('Applied function named "{}" does not exist!'.format(attr))

	def folds(self, fold_count, start=0):
		# Note that rows of created Table objects are
		# the same objects as in the original Table.
		# And the method can return even the original object itself.
		if fold_count < 2:
			return [self]
		end = start
		res = []
		for i in range(fold_count):
			begin = end
			if i < fold_count - 1:
				end += int(self.rowcnt/fold_count)
				data = self.rows[begin:end]
				# print('[{}:{}]'.format(begin, end))
			else:
				end = self.rowcnt
				data = self.rows[begin:end] + self.rows[:start]
				# print('[{}:{}] + [:{}]'.format(begin, end, start))
			res.append(Table(self.columns, data, 'Part {} of {}'.format(i+1, self.title)))
		return res

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
		res += ' '.join(map(lambda x: repr_cell(x, quote_strings=True), self.columns[:showcolscnt]))
		if hiddencols:
			res += ' ...'
		for row in self.rows[:showrowscnt]:
			res += '\n' + ' '.join(map(lambda x: repr_cell(x, quote_strings=True), row[:showcolscnt]))
		if hiddenrows:
			res += '\n. . .'
		return res

	def html(self, cut=True):
		showrowscnt, showcolscnt, hiddenrows, hiddencols = self.__need_cut__(cut)
		res = '<table>\n<tr><th>'
		res += '</th><th>'.join(map(lambda x: repr_cell(x), self.columns[:showcolscnt]))
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
		res = '<b>Table</b> object <b>{}</b>, {} columns, {} rows<br>\n'.format(self.title, len(self.columns), len(self.rows))
		res += self.html()
		return res

	def __repr__(self):
		return self.__str__()

	def __len__(self):
		"""Returns number of cells - product of number of rows and columns."""
		return self.rowcnt * self.colcnt
