__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'projects@aivanf.com'

from datetime import date, datetime
import numbers, math, functools
from .utils import call_with_numbers_only, call_with_existing_only


def mode(lst):
	return max(set(lst), key=lst.count)


def percentile(lst, percent=0.5):
	"""
	Find the percentile of a list of values.

	@parameter lst - is a list of values.
	@parameter percent - a float value from 0.0 to 1.0.

	@return - the percentile of the values
	"""
	lst = sorted(lst)
	k = (len(lst)-1) * percent
	f = math.floor(k)
	c = math.ceil(k)
	if f == c:
		return lst[int(k)]
	d0 = lst[int(f)] * (c-k)
	d1 = lst[int(c)] * (k-f)
	return d0+d1


Q1 = functools.partial(percentile, percent=0.25)
Q2 = functools.partial(percentile, percent=0.5)
Q3 = functools.partial(percentile, percent=0.75)
median = Q2


def avg(lst):
	# TODO: use call_with_numbers_only ?
	if len(lst) > 0:
		return 1.0 * sum(lst) / len(lst)
	else:
		return 0


def std(lst, ddof=0, mean=None):
	"""Calculates the population standard deviation by default;
	specify ddof=1 to compute the sample standard deviation."""
	if len(lst) >= 1+ddof:
		if mean is None:
			mean = avg(lst)
		# Sum of square deviations
		ss = sum((x-mean)**2 for x in lst)
		# Dispersion
		disp = ss / (len(lst) - ddof)
		return disp ** 0.5
	else:
		return 0


def nunique(lst):
	return len(set(lst))


aggfuns = {
	'avg': call_with_numbers_only(avg),
	'mean': call_with_numbers_only(avg),
	'mode': call_with_numbers_only(mode),
	'middle': call_with_numbers_only(median),
	'median': call_with_numbers_only(median),
	'q1': call_with_numbers_only(Q1),
	'q2': call_with_numbers_only(Q2),
	'q3': call_with_numbers_only(Q3),
	'std': call_with_numbers_only(std),
	'sum': call_with_numbers_only(sum),
	'min': call_with_existing_only(min),
	'max': call_with_existing_only(max),
	'count': len,
	'first': lambda x: x[0] if len(x) > 0 else None,
	'last': lambda x: x[-1] if len(x) > 0 else None,
	'nunique': nunique,
}


def makeStr(val, default=None):
	if isinstance(val, str):
		return val
	elif default is None:
		return str(val)
	else:
		return default


def tryInt(val, default=0):
	try:
		return int(val)
	except:
		return default


def tryFloat(val, default=0):
	try:
		return float(val)
	except:
		return default


def tryDatetime(val, default=None):
	if isinstance(val, datetime):
		return val
	if not isinstance(val, str):
		return default
	try:
		return datetime.strptime(val[:19], '%Y-%m-%d %H:%M:%S')
	except ValueError:
		pass
	try:
		return datetime.strptime(val[:16], '%Y-%m-%d %H:%M')
	except ValueError:
		pass
	return default


def tryDate(val, default=None):
	if isinstance(val, date):
		return val
	if not isinstance(val, str):
		return default
	try:
		if len(val) > 8:
			val = val[:10]
			if '/' in val:
				return datetime.strptime(val, '%d/%m/%Y').date()
			elif '-' in val:
				return datetime.strptime(val, '%Y-%m-%d').date()
			elif '.' in val:
				return datetime.strptime(val, '%d.%m.%Y').date()
		elif len(val) > 6:
			val = val[:8]
			if '/' in val:
				return datetime.strptime(val, '%m/%d/%y').date()
	except ValueError:
		pass
	return default


def none_to(val, default=0):
	return default if val is None else val


typefuns = {
	'str': makeStr,
	'int': tryInt,
	'float': tryFloat,
	'date': tryDate,
	'datetime': tryDatetime,
	'none_to': none_to,
}


def isnull(val):
	return val is None


def lengths(val, strings_only=False):
	if strings_only and not isinstance(val, str):
		return None
	return len(str(val))


def isin(val, other):
	return val in other


applyfuns = {
	'isnull': isnull,
	'lengths': lengths,
	'isin': isin,
	'istype': isinstance,
	'isinstance': isinstance,
}


def parse_value(val, empty=None):
	res = tryInt(val, None)
	if res is not None:
		return res
	else:
		res = tryFloat(val, None)
		if res is not None:
			return res
		else:
			res = tryDatetime(val, None)
			if res is not None:
				return res
			else:
				res = tryDate(val, None)
				if res is not None:
					return res
	res = str(val).lower()
	if res == 'none' or res == 'null' or len(res) == 0:
		return empty
	return val


def parse_row(lst, empty=None):
	"""Takes a list of strings and returns list of values with different types."""
	for i in range(len(lst)):
		lst[i] = parse_value(lst[i])
	return lst
