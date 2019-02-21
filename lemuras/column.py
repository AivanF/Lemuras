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

import operator
from datetime import date, datetime
from .processing import applyfuns, typefuns, aggfuns


class Column(object):
	def __init__(self, values=None, title='NoName', table=None, source_name=None):
		if values is None and table is None:
			raise ValueError('Either values or table must be not None!')
		if values is not None and table is not None:
			raise ValueError('Either values or table must be given, not both of them!')
		if table is not None and source_name is None:
			raise ValueError('Table requres source_name argument!')
		self.values = values
		self.title = title
		self.table = table
		self.source_name = source_name

	def get_values(self):
		if self.values is not None:
			return self.values
		else:
			column_index = self.table.column_indices[self.source_name]
			return map(lambda row: row[column_index], self.table.rows)

	def get_value(self, row_index):
		if self.values is not None:
			return self.values[row_index]
		else:
			column_index = self.table.column_indices[self.source_name]
			return self.table.rows[row_index][column_index]

	def set_value(self, row_index, value):
		if self.values is not None:
			self.values[row_index] = value
		else:
			column_index = self.table.column_indices[self.source_name]
			self.table.rows[row_index][column_index] = value

	def __getitem__(self, index):
		return self.get_value(index)

	def __setitem__(self, row_index, value):
		self.set_value(row_index, value)

	def __iter__(self):
		return iter(self.get_values())

	def get_type(self):
		"""Returns column type and max symbols length."""
		# None Int Float String Mixed
		tp = 'n'
		# varchar length
		ln = 0

		cnt = len(self)
		if cnt > 4096:
			cnt = int(cnt / 3)
		elif cnt > 2048:
			cnt = int(cnt / 2)

		for index, el in enumerate(self.get_values()):
			if index >= cnt:
				break
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

	def folds(self, fold_count, start=0):
		# Note that the method can return even the original Column itself.
		if fold_count < 2:
			return [self]
		end = start
		res = []
		values = list(self.get_values())
		for i in range(fold_count):
			begin = end
			if i < fold_count - 1:
				end += int(len(values)/fold_count)
				data = values[begin:end]
				# print('[{}:{}]'.format(begin, end))
			else:
				end = len(values)
				data = values[begin:end] + values[:start]
				# print('[{}:{}] + [:{}]'.format(begin, end, start))
			res.append(Column(data, 'Part {} of {}'.format(i+1, self.title)))
		return res

	def apply(self, task, *args, **kwargs):
		""" Several cases are possible:
		1. Changes column values types if type name is given.
		The following are supported: str, int, float, date, datetime.
		All the types can take a default value.
		2. Returns new columns with applied function.
		"""
		# Default KW argument after variable with positional arguments
		# is allowed in Python 3 only, not Python 2
		# apply(self, task, *args, separate=False, **kwargs)
		# So, we have to handle it manually
		separate = kwargs.pop('separate', None)

		if isinstance(task, str):
			if task in typefuns:
				task = typefuns[task]
				separate = False if separate is None else separate
			elif task in applyfuns:
				task = applyfuns[task]
				separate = True if separate is None else separate
			else:
				raise ValueError('Applied function named "{}" does not exist!'.format(task))
		else:
			# Custom functions lead to new Column object by default
			separate = True if separate is None else separate

		if separate:
			res = []
			for i in range(len(self)):
				res.append(task(self.get_value(i), *args, **kwargs))
			return Column(res, self.title)
		else:
			for i in range(len(self)):
				self.set_value(i, task(self.get_value(i), *args, **kwargs))
			return self

	def calc(self, task, *args, **kwargs):
		""" Calculates an aggregated value by function or task name.
		"""
		if isinstance(task, str):
			if task in aggfuns:
				task = aggfuns[task]
			else:
				raise ValueError('Applied function named "{}" does not exist!'.format(task))
		return task(list(self.get_values()), *args, **kwargs)

	def __getattr__(self, attr):
		if attr in applyfuns or attr in typefuns:
			def inner(*args, **kwargs):
				return self.apply(attr, *args, **kwargs)
			return inner
		elif attr in aggfuns:
			def inner(*args, **kwargs):
				return self.calc(attr, *args, **kwargs)
			return inner
		else:
			raise AttributeError('Applied function named "{}" does not exist!'.format(attr))


	def copy(self):
		"""Returns new Column as a deep copy of this one"""
		return Column(values=list(self.get_values()), title=self.title)

	def _repr_html_(self):
		n = len(self)
		ns = False
		if n > 12:
			n = 10
			ns = True
		res = '<b>Column</b> object, title: "{}" values: {}.'.format(self.title, list(self.get_values())[:n])
		if ns:
			res += ' . .'
		return res

	def __repr__(self):
		n = len(self)
		ns = False
		if n > 12:
			n = 10
			ns = True
		res = '- Column object, title: "{}" values: {}.'.format(self.title, list(self.get_values())[:n])
		if ns:
			res += ' . .'
		return res

	def __len__(self):
		if self.values is not None:
			return len(self.values)
		else:
			return self.table.rowcnt

	def __contains__(self, item):
		return item in self.get_values()

	def __operator1__(self, operator):
		return Column([operator(self.get_value(i)) for i in range(la)])

	def __operator2__(self, other, operator):
		if isinstance(other, Column):
			if len(self) == len(other):
				return Column([operator(self.get_value(i), other[i]) for i in range(len(self))])
			else:
				raise ValueError('Others Column len must be the same')
		else:
			return Column([operator(el, other) for el in self.get_values()])

	def __not__(self):
		return self.__operator1__(other, operator.__not__)

	def __invert__(self):
		return self.__operator1__(other, operator.__invert__)

	def __abs__(self):
		return self.__operator1__(other, operator.__abs__)

	def __and__(self, other):
		return self.__operator2__(other, operator.__and__)

	def __or__(self, other):
		return self.__operator2__(other, operator.__or__)

	def __xor__(self, other):
		return self.__operator2__(other, operator.__xor__)

	def __add__(self, other):
		return self.__operator2__(other, operator.__add__)

	def __sub__(self, other):
		return self.__operator2__(other, operator.__sub__)

	def __mul__(self, other):
		return self.__operator2__(other, operator.__mul__)

	def __pow__(self, other):
		return self.__operator2__(other, operator.__pow__)

	def __mod__(self, other):
		return self.__operator2__(other, operator.__mod__)

	def __truediv__(self, other):
		return self.__operator2__(other, operator.__truediv__)

	def __concat__(self, other):
		return self.__operator2__(other, operator.__concat__)

	def __and__(self, other):
		return self.__operator2__(other, operator.__and__)

	def __gt__(self, other):
		return self.__operator2__(other, operator.__gt__)

	def __lt__(self, other):
		return self.__operator2__(other, operator.__lt__)

	def __ge__(self, other):
		return self.__operator2__(other, operator.__ge__)

	def __le__(self, other):
		return self.__operator2__(other, operator.__le__)

	def __eq__(self, other):
		return self.__operator2__(other, operator.__eq__)

	def __ne__(self, other):
		return self.__operator2__(other, operator.__ne__)
