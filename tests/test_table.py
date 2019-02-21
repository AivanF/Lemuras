from lemuras import Table, Column
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 1, 12, None],
	['B', 4, 12, 84505505151],
	['A', 3, 10, '+31415926535'],
	['B', 6, 14, ''],
	['A', 4, 10, '23816326412'],
	['A', 2, 12, 0],
]
df1 = Table(cols, rows)
shift = 4


class TestLemurasTable(unittest.TestCase):
	def test_loc_linked(self):
		df2 = df1.copy()
		# Must be not separate
		part = df2.loc(df2['size'].isin((2,4)))
		self.assertEqual(part.rowcnt, 3)
		part.row(0)['size'] += shift
		# df2 must be changed
		self.assertEqual(df2['size'].sum(), df1['size'].sum() + shift)

	def test_loc_separate(self):
		df2 = df1.copy()
		# A separate table
		part = df2.loc(df2['size'].isin((2,4)), separate=True)
		part.row(0)['size'] += shift
		# df2 must not be changed
		self.assertEqual(df2['size'].sum(), df1['size'].sum())

	def test_loc_exception(self):
		with self.assertRaises(ValueError) as context:
			ch = df1['size'].isin((2,4))
			ch.values.pop()
			part = df1.loc(ch)
			print(part)
		self.assertTrue('must be the same' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			ch = df1['size'].isin((2,4)).values
			part = df1.loc(ch)
			print(part)
		self.assertTrue('Column' in str(context.exception))

	def test_calc(self):
		res = df1.calc(lambda row: row['size']*row['weight'])
		self.assertEqual(res.sum(), 238)

	def test_sort_iterate(self):
		df2 = df1.copy()
		df2.sort('weight')
		last = df2['weight'].min()
		for row in df2:
			self.assertTrue(last <= row['weight'])
			last = row['weight']
		df2.sort(['weight'], asc=[False])
		last = df2['weight'].max()
		for row in df2:
			self.assertTrue(last >= row['weight'])
			last = row['weight']

	def test_rename(self):
		df2 = df1.copy()
		initial_length = len(df2.columns)
		old = 'size'
		new = 'sz'
		df2.rename(old, new)
		self.assertEqual(len(df2.column_indices), initial_length)
		self.assertEqual(df2.columns[df2.column_indices[new]], new)

	def test_delete_column(self):
		df2 = df1.copy()
		deleted = 'size'
		initial_length = len(df2.columns)
		df2.delete_column(deleted)
		self.assertEqual(len(df2.column_indices), initial_length-1)
		self.assertEqual(len(df2.columns), initial_length-1)
		self.assertEqual(len(df2.rows[0]), initial_length-1)
		self.assertEqual(len(df2.rows[-1]), initial_length-1)

	def test_set_column(self):
		df2 = df1.copy()
		data = df2['weight']-df2['size']
		df2['size'] = data
		df2['size'] = data.values
		data.values = data.values[1:]
		with self.assertRaises(ValueError) as context:
			df2['size'] = data
		self.assertTrue('len' in str(context.exception))
		
		with self.assertRaises(ValueError) as context:
			df2['size'] = 'test,sample data'
		self.assertTrue('Column' in str(context.exception))

	def test_row(self):
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

		for row in df2:
			for i, el in enumerate(row):
				self.assertEqual(el, row[i])
