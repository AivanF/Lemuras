import unittest
from lemuras import Table, Row
from .sample_data import cols, rows, df1


class TestLemurasRows(unittest.TestCase):
	def test_basic(self):
		df2 = df1.copy()

		# Must pass without exceptions
		df2.row(df2.rowcnt-1)
		df2.row(-df2.rowcnt)

		with self.assertRaises(IndexError) as context:
			df2.row(df2.rowcnt)

		with self.assertRaises(IndexError) as context:
			df2.row(-df2.rowcnt-1)

		with self.assertRaises(IndexError) as context:
			df2.row(111)

		with self.assertRaises(IndexError) as context:
			df2.row('lol')

		with self.assertRaises(KeyError) as context:
			df2.row(1)['lol']

		with self.assertRaises(IndexError) as context:
			df2.row(1)[111]

		row = df2.row(1)
		self.assertEqual(len(row), df2.colcnt)
		self.assertEqual(row.colcnt, df2.colcnt)
		self.assertEqual(row.columns, df2.columns)
		self.assertTrue(isinstance(row.get_type()[0], str))

		with self.assertRaises(ValueError) as context:
			row.calc('random_name')

		with self.assertRaises(AttributeError) as context:
			x = row.random_name

		for row in df2:
			for i, el in enumerate(row):
				self.assertEqual(el, row[i])

		self.assertTrue(isinstance(df1.row(0)._repr_html_(), str))
		self.assertTrue(isinstance(df1.row(-1).__repr__(), str))

	def test_linked(self):
		# Changing value of linked row
		df2 = df1.copy()
		change = 5
		was = df2['size'].sum()
		r = df2.row(0)
		r['size'] = r['size'] + change
		self.assertEqual(was + change, df2['size'].sum())


	def test_separated(self):
		# Changing value of separated row
		df2 = df1.copy()
		was = df2['size'].sum()
		r = df2.row(0).copy()
		r['size'] = r['size'] + 11
		self.assertEqual(was, df2['size'].sum())

	def test_iter(self):
		# Nested loops over single object must work
		r = Row(values=[2, 3])
		# 2*2 + 2*3 + 3*2 + 3*3 = 4 + 12 + 9
		self.assertEqual(sum((a*b for a in r for b in r)), 25)
