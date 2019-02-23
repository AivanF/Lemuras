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


class TestLemurasTablePivot(unittest.TestCase):
	def test_pivot_main(self):
		df2 = df1.pivot('x', 'y', 'val', 0)
		self.assertEqual(df2.colcnt, df1['x'].nunique() + 1)
		self.assertEqual(df2.rowcnt, df1['y'].nunique())
		self.assertEqual(df2.loc(df2['y']=='c').row().sum(), df1.loc(df1['y']=='c')['val'].sum())
		self.assertEqual(df2.sum()['sum'].sum(), df1['val'].sum())
		self.assertEqual(df2.find_types().find({'Column':'y'})['Type'], 's')

	def test_not_str_columns(self):
		df2 = df1.pivot('x', 'y', 'val', 0, str_columns=False)
		self.assertTrue(isinstance(df2.columns[-1], int))
		self.assertTrue(df2.columns[-1] in df2.column_indices)
		self.assertEqual(len(df2.columns), len(df2.column_indices))
