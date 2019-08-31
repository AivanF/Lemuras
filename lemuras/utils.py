__author__ = 'AivanF'
__copyright__ = 'Copyright 2019, AivanF'
__contact__ = 'projects@aivanf.com'

import datetime
import numbers
import sys

if sys.version_info[0] == 2:
	from io import BytesIO
	file_container = lambda x: BytesIO(bytes(x))
	main_str = basestring
else:
	from io import StringIO
	file_container = lambda x: StringIO(x)
	main_str = str

try:
	from bs4 import BeautifulSoup
except ImportError:
	BeautifulSoup = None


# LAmbda LEngth POsitive
lalepo = lambda x: len(x) > 0

numbers_only = lambda lst: [x for x in lst if isinstance(x, numbers.Number)]

existing_only = lambda lst: [x for x in lst if x is not None]


def call_with_numbers_only(task):
	"""Returns a function whuch takes a list and executes
	argument function with numbers from that list.
	"""
	def inner(lst):
		lst = numbers_only(lst)
		if len(lst) > 0:
			return task(lst)
		else:
			return None
	return inner


def call_with_existing_only(task):
	"""Returns a function whuch takes a list and executes
	argument function with not-None values from that list.
	"""
	def inner(lst):
		lst = existing_only(lst)
		if len(lst) > 0:
			return task(lst)
		else:
			return None
	return inner


def jsonable(o):
	return isinstance(o, str) or isinstance(o, int) or isinstance(o, float) or isinstance(o, list) or isinstance(o, tuple) or isinstance(o, dict)


def list_of_lists(cnt):
	return [[] for _ in range(cnt)]


def iscollection(x):
	return isinstance(x, list) or isinstance(x, tuple) or isinstance(x, set)


def repr_cell(x, quote_strings=False):
	if isinstance(x, datetime.date):
		return str(x)
	if not quote_strings and isinstance(x, main_str):
		return x
	return repr(x)


def get_type(data, limit=0):
	"""Returns data type and max symbols length."""
	# None Int Float String Mixed
	tp = 'n'
	# varchar length
	ln = 0

	for index, el in enumerate(data):
		if limit > 0 and index > limit:
			break
		ln = max(ln, len(str(el)))

		if isinstance(el, int):
			kind = 'i'
		elif isinstance(el, float):
			kind = 'f'
		elif isinstance(el, datetime.datetime):
			kind = 't'
		elif isinstance(el, datetime.date):
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
