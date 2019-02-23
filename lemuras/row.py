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

from .utils import repr_cell, get_type
from .processing import aggfuns, typefuns, applyfuns


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

	def get_type(self):
		"""Returns row type and max symbols length."""
		return get_type(self.table.rows[self.row_index])

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

	def _repr_html_(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.table.rows[self.row_index])
		res = '<b>Row</b> {} of table <b>{}</b><br>\n[{}]'.format(self.row_index, self.table.title, ','.join(values))
		return res

	def __len__(self):
		"""Returns number of columns."""
		return self.table.colcnt

	def __str__(self):
		values = map(lambda x: repr_cell(x, quote_strings=True), self.table.rows[self.row_index])
		return '- Row {} of table "{}"\n[{}]'.format(self.row_index, self.table.title, ','.join(values))

	def __repr__(self):
		return self.__str__()
