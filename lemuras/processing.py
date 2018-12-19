__author__ = 'AivanF'
__copyright__ = 'Copyright 2018, AivanF'
__contact__ = 'projects@aivanf.com'

from datetime import date, datetime
import numbers
from .utils import call_with_numbers_only


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


typefuns = {
	'str': makeStr,
	'int': tryInt,
	'float': tryFloat,
	'date': tryDate,
	'datetime': tryDatetime,
}


def parse_value(val, empty=None):
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
	if v == 'none' or v == 'null' or len(v) == 0:
		return empty
	return val


def parse_row(lst, empty=None):
	"""Takes a list of strings and returns list of values with different types."""
	for i in range(len(lst)):
		lst[i] = parse_value(lst[i])
	return lst
