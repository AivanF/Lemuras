from lemuras import Table
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 1, 12, '+79360360193'],
	['B', 4, 12, 84505505151],
	['A', 3, 10, '31415926535'],
	['B', 6, 14, 'None'],
	['A', 4, 15, '23816326412'],
	['A', 2, 11, 0],
]
df1 = Table(cols, rows, 'Sample')


class TestLemurasJson(unittest.TestCase):
	def test_save_load(self):
		txt = df1.to_json(pretty=False)
		df2 = Table.from_json(txt)
		self.assertEqual(df2.columns, cols)
		self.assertEqual(df2.rowcnt, len(rows))
		self.assertEqual(df2['weight'].sum(), 74)
