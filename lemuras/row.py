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

from .utils import repr_cell, get_type
from .processing import aggfuns, typefuns, applyfuns


class Row(object):
	def __init__(self, table=None, row_index=None, values=None):
		if values is None:
			if table is None or row_index is None:
				raise ValueError('Both table and row_index must be set!')
		else:
			if table is not None:
				raise ValueError('Either values or table must be not None!')
		self.table = table
		self.row_index = row_index
		self.idx = 0
		self.values = values

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

	def get_values(self):
		if self.values is not None:
			return self.values
		else:
			return map(lambda column: self[column], self.columns)

	def get_value(self, column):
		if self.values is not None:
			# TODO: add strings support
			return self.values[column]
		else:
			return self.table.cell(column, self.row_index)

	def set_value(self, column, value):
		if self.values is not None:
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
		return task(self.table.rows[self.row_index], *args, **kwargs)

	def __getattr__(self, attr):
		if attr in aggfuns:
			def inner(*args, **kwargs):
				return self.calc(attr, *args, **kwargs)
			return inner
		else:
			raise AttributeError('Applied function named "{}" does not exist!'.format(attr))

	def copy(self):
		"""Returns new Row as a deep copy of this one"""
		return Row(values=list(self.get_values()), row_index=self.row_index)

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
