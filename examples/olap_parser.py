# coding=utf-8
__author__ = 'AivanF'
__copyright__ = 'Copyright 2019, AivanF'
__contact__ = 'projects@aivanf.com'

import datetime
from collections import namedtuple
from io import StringIO
import csv

from lemuras import Table, Column
from lemuras.processing import typefuns
from lemuras.utils import main_str

# Set cache=True to indicate a grouped column
# It values will be saved and used instead of empty cells
ColumnData = namedtuple('ColumnData', 'name type cache default')


class ParserError(Exception):
	pass


def ColumnData_make(**data):
	res = {'name': '-', 'type': 'str', 'cache': True}
	res.update(data)
	if 'default' not in res:
		if res['type'] == 'str':
			res['default'] = ''
		else:
			res['default'] = None
	return ColumnData(**res)


class OlapParser(object):
	def __init__(self):
		self.skip_header_rows = 0
		self.meta_header_rows = 0
		self.allow_longer_rows = False
		self.skip_bad_rows = False
		self.cascade_caching = True
		self.row_limit = -1

	def describe_column(self, column_index, raw_value, meta):
		# Should be overrided, must return None or ColumnData
		return ColumnData_make(name='c'+str(column_index), type='str')

	def check_skip(self, line, row):
		# Should be overrided to deterime aggregated rows
		return False

	def validate_columns(self):
		# Can be overrided to throw exceptions
		pass

	def parse_row(self, row, typefuns=typefuns):
		if self.check_skip(' '.join(map(str,row)), row):
			return
		if self.row_index < self.skip_header_rows:
			return
		row = [str(value).strip() for value in row]

		if len(self.meta_header) < self.meta_header_rows:
			# Upper header row
			self.meta_header.append(row)

		elif self.columns is None:
			# Header row
			self.columns = []
			self.cache = []
			for column_index, raw_value in enumerate(row):
				meta = []
				for line in self.meta_header:
					value = ''
					for i, cur in enumerate(line):
						if i > column_index:
							break
						if len(cur) > 0:
							value = cur
					meta.append(value)
				col_des = self.describe_column(column_index, raw_value, meta)
				if col_des is not None:
					assert isinstance(col_des, ColumnData)
					if isinstance(col_des.type, main_str):
						if col_des.type not in typefuns:
							raise ParserError('Bad column type {}'.format(col_des.type))
					if col_des.name in self.columns_dict:
						raise ParserError('Repeating column "{}"'.format(col_des.name))
					self.res_columns.append(col_des.name)
					self.columns_dict[col_des.name] = column_index
					self.cache.append(col_des.default)
				else:
					self.cache.append(None)
				self.columns.append(col_des)
			self.validate_columns()
			self.colcnt = len(self.columns)
			if len(self.res_columns) == 0:
				raise ParserError('No columns selected!')

		else:
			# Usual data row
			if len(row) != self.colcnt:
				if self.skip_bad_rows:
					if len(row) < self.colcnt or (len(row) > self.colcnt and not self.allow_longer_rows):
						return
				else:
					if len(row) < self.colcnt or (len(row) > self.colcnt and not self.allow_longer_rows):
						txt = 'Row {} has len {} while there are {} columns!\nColumns: {}\nRow: {}'
						txt = txt.format(self.row_index, len(row), self.colcnt, self.columns, row)
						raise ParserError(txt)
				row = row[:self.colcnt]
			res_row = []
			for column_index, raw_value in enumerate(row):
				col_des = self.columns[column_index]
				if col_des is not None:
					if col_des.cache and len(raw_value) == 0:
						value = self.cache[column_index]
					else:
						if isinstance(col_des.type, main_str):
							# Builting parsing
							value = typefuns[col_des.type](raw_value)
						else:
							# Custom parsing
							value = col_des.type(raw_value)
						if col_des.cache:
							self.cache[column_index] = value
							if self.cascade_caching:
								# Empty cache of columns on the right
								for ind in range(column_index+1, len(self.cache)):
									if self.cache[ind] is None:
										continue
									self.cache[ind] = self.columns[ind].default
					res_row.append(value)
			self.res_rows.append(res_row)

	def _parse_init(self):
		self.columns = None
		self.columns_dict = {}
		self.meta_header = []
		self.colcnt = 0
		self.res_columns = []
		self.res_rows = []
		self.cache = None

	def parse_csv(self, fl, delimiter=None):
		self._parse_init()
		csvreader = csv.reader(fl, delimiter=delimiter, quotechar='"')

		for self.row_index, row in enumerate(csvreader):
			self.parse_row(row)
			if self.row_limit > 0 and self.row_index > self.row_limit:
				break
		return Table(self.res_columns, self.res_rows)

	def parse_xls(self, bs):
		import xlrd

		def xlrd_parse_date(value):
			# XLRD returns dates as strange timestamps which must be properly parsed
			return datetime.datetime(*xlrd.xldate_as_tuple(float(value), book.datemode)).date()

		book = xlrd.open_workbook(file_contents=bs)
		first_sheet = book.sheet_by_index(0)
		self._parse_init()
		self.row_index = 0
		_typefuns = {}
		_typefuns.update(typefuns)
		_typefuns['date'] = xlrd_parse_date

		while True:
			try:
				row = first_sheet.row_values(self.row_index)
				self.parse_row(row, _typefuns)
				self.row_index += 1
				if self.row_limit > 0 and self.row_index > self.row_limit:
					break
			except IndexError:
				break
		return Table(self.res_columns, self.res_rows)

	def parse(self, fl, filename):
		# fl must be None or binary file-like object
		opened = False
		if fl == None:
			opened = True
			fl = open(filename, 'rb+')
		bs = fl.read()
		if opened:
			fl.close()
		def sfl():
			return StringIO(bs.decode('UTF-8'))

		ext = filename.split('.')[-1]
		if 'csv' == ext:
			res = self.parse_csv(sfl(), ',')
		elif 'tsv' == ext:
			res = self.parse_csv(sfl(), '\t')
		elif 'xls' == ext:
			res = self.parse_xls(bs)
		else:
			raise ParserError('Extension of {} is unsupported'.format(filename))
		res.title = filename.split('/')[-1]
		return res
