import unittest
from lemuras import Table
from .sample_data import cols, rows, df1


class TestLemurasJson(unittest.TestCase):
	def test_json_list(self):
		txt = df1.to_json(pretty=False)
		df2 = Table.from_json(txt)
		self.assertEqual(df2.columns, cols)
		self.assertEqual(df2.rowcnt, df1.rowcnt)
		self.assertEqual(df2['weight'].sum(), df1['weight'].sum())

	def test_json_list_pretty(self):
		txt = df1.to_json(pretty=True)
		df2 = Table.from_json(txt)
		self.assertEqual(df2.columns, cols)
		self.assertEqual(df2.rowcnt, df1.rowcnt)
		self.assertEqual(df2['weight'].sum(), df1['weight'].sum())

	def test_json_dict(self):
		txt = df1.to_json(as_dict=True, pretty=False)
		df2 = Table.from_json(txt)
		self.assertEqual(df2.columns, cols)
		self.assertEqual(df2.rowcnt, df1.rowcnt)
		self.assertEqual(df2['weight'].sum(), df1['weight'].sum())

	def test_json_dict_pretty(self):
		txt = df1.to_json(as_dict=True, pretty=True)
		df2 = Table.from_json(txt)
		self.assertEqual(df2.columns, cols)
		self.assertEqual(df2.rowcnt, df1.rowcnt)
		self.assertEqual(df2['weight'].sum(), df1['weight'].sum())
