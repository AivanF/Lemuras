import unittest
from lemuras import Table, Column

cols = ['x', 'y', 'val']
rows = [
	[0, 'c', 3],
	[2, 'b', 7],
	[1, 'a', 2],
	[4, 'c', 2],
]
df1 = Table(cols, rows)

cols = ['x', 'y', 'val']
rows = [
	[1, 'a', 3],
	[0, 'c', 3],
	[2, 'b', 7],
	[0, 'c', 1],
	[1, 'a', 2],
	[4, 'c', 2],
]
df2 = Table(cols, rows)


class TestLemurasTablePivot(unittest.TestCase):
	def test_pivot_main(self):
		res = df1.pivot('x', 'y', 'val', 0)
		self.assertEqual(res.colcnt, df1['x'].nunique() + 1)
		self.assertEqual(res.rowcnt, df1['y'].nunique())
		self.assertEqual(res.loc(res['y']=='c').row().sum(), df1.loc(df1['y']=='c')['val'].sum())
		self.assertEqual(res.sum()['sum'].sum(), df1['val'].sum())
		self.assertEqual(res.find_types().find({'Column':'y'})['Type'], 's')

	def test_not_str_columns(self):
		res = df1.pivot('x', 'y', 'val', 0, str_columns=False)
		self.assertTrue(isinstance(res.columns[-1], int))
		self.assertTrue(res.columns[-1] in res.column_indices)
		self.assertEqual(len(res.columns), len(res.column_indices))

	def test_pivot_task_sum(self):
		res = df2.pivot('x', 'y', 'val', 0, task='sum')
		self.assertEqual(res.find({'y': 'a'}).sum(), 5)
		self.assertEqual(res.find({'y': 'b'}).sum(), 7)
		self.assertEqual(res.find({'y': 'c'}).sum(), 6)

	def test_pivot_task_min(self):
		res = df2.pivot('x', 'y', 'val', 0, task='min')
		self.assertEqual(res.find({'y': 'a'}).sum(), 2)
		self.assertEqual(res.find({'y': 'b'}).sum(), 7)
		self.assertEqual(res.find({'y': 'c'}).sum(), 3)

	def test_pivot_task_count(self):
		res = df2.pivot('x', 'y', 'val', 0, task='count')
		self.assertEqual(res.sum()['sum'].sum(), df2.rowcnt)
