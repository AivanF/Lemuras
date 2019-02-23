import unittest
from lemuras import Table

cols1 = ['type', 'size', 'weight', 'tel']
rows1 = [
	['A', 2, 12, '+79360360193'],
	['B', 1, 12, 84505505151],
	['D', 1, 10, '31415926535'],
	['B', 2, 14, ''],
	['A', 1, 15, '23816326412'],
	['D', 2, 11, 0],
]
df1 = Table(cols1, rows1)

cols2 = ['type', 'size', 'cost']
rows2 = [
	['A', 2, 3.1415],
	['B', 1, 2.7182],
	['C', 2, 1.2345],
	['D', 1, 1.2345],
]
df2 = Table(cols2, rows2)

cnt_inner = 3
cnt_left = 3
cnt_right = 1


class TestLemurasTableMerge(unittest.TestCase):
	def test_outer(self):
		df3 = Table.merge(df1, df2, ['type', 'size'], 'outer')
		self.assertEqual(df3.rowcnt, cnt_inner+cnt_left+cnt_right)
		self.assertEqual(df3.columns, ['type', 'size', 'weight', 'tel', 'cost'])
		self.assertEqual(df3.nunique()[1].sum(), 23)
		self.assertEqual(df3['weight'].sum(), 74)

	def test_inner(self):
		df3 = Table.merge(df1, df2, ['type', 'size'], 'inner')
		self.assertEqual(df3.rowcnt, cnt_inner)
		self.assertEqual(df3.columns, ['type', 'size', 'weight', 'tel', 'cost'])
		self.assertEqual(df3.nunique()[1].sum(), 13)
		self.assertEqual(df3['weight'].sum(), 34)

	def test_left(self):
		df3 = Table.merge(df1, df2, ['type', 'size'], 'left')
		self.assertEqual(df3.rowcnt, cnt_inner+cnt_left)
		self.assertEqual(df3.columns, ['type', 'size', 'weight', 'tel', 'cost'])
		self.assertEqual(df3.nunique()[1].sum(), 20)
		self.assertEqual(df3['weight'].sum(), 74)

	def test_right(self):
		df3 = Table.merge(df1, df2, ['type', 'size'], 'right')
		self.assertEqual(df3.rowcnt, cnt_inner+cnt_right)
		self.assertEqual(df3.columns, ['type', 'size', 'weight', 'tel', 'cost'])
		self.assertEqual(df3.nunique()[1].sum(), 16)
		self.assertEqual(df3['weight'].sum(), 34)
