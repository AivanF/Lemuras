__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'projects@aivanf.com'

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
	res = []
	for i in range(cnt):
		res.append([])
	return res


def iscollection(x):
	return isinstance(x, list) or isinstance(x, tuple) or isinstance(x, set)
