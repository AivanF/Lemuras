from lemuras import Table
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 2, 12, '+79360360193'],
	['B', 1, 12, 84505505151],
	['D', 1, 10, '31415926535'],
	['B', 2, 14, ''],
	['A', 1, 15, '23816326412'],
	['D', 2, 11, 0],
]
df1 = Table(cols, rows)

cols = ['type', 'size', 'cost']
rows = [
	['A', 2, 3.1415],
	['B', 1, 2.7182],
	['C', 2, 1.2345],
	['D', 1, 1.2345],
]
df2 = Table(cols, rows)


class TestLemurasMerge(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(TestLemurasMerge, self).__init__(*args, **kwargs)
		self.df3 = Table.merge(df1, df2, ['type', 'size'], 'outer')

	def test_columns(self):
		self.assertEqual(self.df3.columns, ['type', 'size', 'weight', 'tel', 'cost'])

	def test_values(self):
		self.assertEqual(self.df3.nunique()[1].sum(), 23)
		self.assertEqual(self.df3['weight'].sum(), 74)
