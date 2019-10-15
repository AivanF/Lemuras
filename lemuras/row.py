__author__ = 'AivanF'
__copyright__ = 'Copyright 2019, AivanF'
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

from .utils import main_str, repr_cell, get_type
from .processing import aggfuns, typefuns, applyfuns


class Row(object):
	def __init__(self, table=None, row_index=None, values=None, columns=None):
		if values is None:
			if table is None or row_index is None:
				raise ValueError('Both table and row_index must be set!')
		else:
			if table is not None:
				raise ValueError('Either values or table must be not None!')
			if columns is None:
				columns = list(map(str, range(len(values))))
		self.table = table
		self.row_index = row_index
		self.values = values
		self.column_names = columns

	def __iter__(self):
		return iter(self.get_values())

	@property
	def colcnt(self):
		if self.values is not None:
			return len(self.values)
		else:
			return self.table.colcnt

	@property
	def columns(self):
		if self.values is not None:
			return self.column_names
		else:
			return self.table.columns

	def get_values(self):
		if self.values is not None:
			return self.values
		else:
			return map(lambda column: self[column], self.columns)

	def get_value(self, column):
		if self.values is not None:
			if isinstance(column, main_str):
				return self.values[self.column_names.index(column)]
			else:
				return self.values[column]
		else:
			return self.table.cell(column, self.row_index)

	def set_value(self, column, value):
		if self.values is not None:
			if isinstance(column, main_str):
				self.values[self.column_names.index(column)] = value
			else:
				self.values[column] = value
		else:
			self.table.set_cell(column, self.row_index, value)

	def __getitem__(self, column):
		return self.get_value(column)

	def __setitem__(self, column, value):
		self.set_value(column, value)

	def get_type(self):
		"""Returns row type and max symbols length."""
		return get_type(self.get_values())

	def calc(self, task, *args, **kwargs):
		""" Calculates an aggregated value by function or task name.
		"""
		if isinstance(task, str):
			if task in aggfuns:
				task = aggfuns[task]
			else:
				raise ValueError('Applied function named "{}" does not exist!'.format(task))
		return task(self.get_values(), *args, **kwargs)

	def __getattr__(self, attr):
		if attr in aggfuns:
			def inner(*args, **kwargs):
				return self.calc(attr, *args, **kwargs)
			return inner
		else:
			raise AttributeError('Applied function named "{}" does not exist!'.format(attr))

	def copy(self):
		"""Returns new Row as a deep copy of this one"""
		return Row(values=list(self.get_values()), row_index=self.row_index, columns=self.columns)

	def _repr_html_(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.table.rows[self.row_index])
		res = '<b>Row</b> {} of table <b>{}</b><br>\n[{}]'.format(self.row_index, self.table.title, ','.join(values))
		return res

	def __len__(self):
		"""Returns number of columns."""
		if self.values is not None:
			return len(self.values)
		else:
			return self.table.colcnt

	def __str__(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.get_values())
		if self.values is None:
			return '- Row {} of table "{}"\n[{}]'.format(self.row_index, self.table.title, ','.join(values))
		else:
			return '- Row independent\n[{}]'.format(','.join(values))

	def __repr__(self):
		return self.__str__()
