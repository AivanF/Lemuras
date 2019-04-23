import unittest
from lemuras import Table, Column
from .sample_data import cols, rows, df1

shift = 4


class TestLemurasTable(unittest.TestCase):
	def test_basic(self):
		self.assertEqual(df1.colcnt, len(cols))
		self.assertEqual(df1.rowcnt, len(rows))
		self.assertEqual(len(df1), len(rows))

		# Nonexistent names must lead to specific error
		# It is important due to __getattr__ overriding
		with self.assertRaises(AttributeError) as context:
			x = df1.random_name

		with self.assertRaises(KeyError) as context:
			x = df1['random_name']

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

	def test_index(self):
		df2 = df1.copy()
		df2.make_index('id')
		self.assertEqual(df2['id'].sum(), 15)

	def test_apply(self):
		self.assertEqual(df1.isnull().sum()['sum'].sum(), 2)

	def test_calc(self):
		res = df1.calc(lambda row: row['size']*row['weight'])
		check = df1['size']*df1['weight']
		self.assertEqual(res.sum(), check.sum())

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

		# It is a different method for adding new column than for replacing and old one
		# So, it must be checked too
		with self.assertRaises(ValueError) as context:
			df2['new'] = data
		self.assertTrue('len' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			df2['new'] = 'test,sample data'
		self.assertTrue('Column' in str(context.exception))

	def test_from_columns(self):
		columns = [
			df1['type'],
			df1['weight'] + df1['size']**2,
		]
		title = 'Random test title'
		df2 = Table.from_columns(columns, title)
		self.assertEqual(df2.rowcnt, df1.rowcnt)
		self.assertEqual(df2.colcnt, len(columns))
		self.assertEqual(df2.title, title)

	def test_find(self):
		self.assertEqual(df1.find({'type':'B', 'weight':12})['tel'], 84505505151)
		self.assertEqual(df1.find({'type':'A', 'weight':7}), None)
		
		found = df1.find_all({'type':'A', 'weight':12})
		self.assertEqual(found.colcnt, df1.colcnt)
		self.assertEqual(found.rowcnt, 2)

		with self.assertRaises(ValueError) as context:
			df1.find(16)
		self.assertTrue('dict' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			df1.find({})
		self.assertTrue('at least' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			df1.find({'fake':5})
		self.assertTrue('name' in str(context.exception))

	def test_folds(self):
		folds = df1.folds(3)
		agg_sum1 = 0
		agg_sum2 = 0
		agg_cnt = 0
		for cur in folds:
			agg_sum1 += cur['size'].sum()
			agg_sum2 += cur['weight'].sum()
			agg_cnt += cur.rowcnt
		self.assertEqual(agg_sum1, df1['size'].sum())
		self.assertEqual(agg_sum2, df1['weight'].sum())
		self.assertEqual(agg_cnt, df1.rowcnt)

		self.assertEqual(df1.folds(1)[0], df1)

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

	def test_delete_row(self):
		df2 = df1.copy()
		df2.delete_row(0)
		df2.delete_row(-1)
		self.assertEqual(df2.rowcnt+2, df1.rowcnt)
		self.assertEqual(df2['size'][0], df1['size'][1])
		self.assertEqual(df2['size'][-1], df1['size'][-2])

	def test_add_row(self):
		df2 = df1.copy()
		with self.assertRaises(ValueError) as context:
			df2.add_row('String')
		self.assertTrue('list' in str(context.exception))
		self.assertTrue('dict' in str(context.exception))

		# Strict mode is on by default
		with self.assertRaises(ValueError) as context:
			df2.add_row({})

		# No error must occur
		df2.add_row({}, strict=False)

		with self.assertRaises(ValueError) as context:
			df2.add_row([])
		self.assertTrue('len' in str(context.exception))

	def test_repr(self):
		self.assertTrue(isinstance(df1._repr_html_(), str))
		self.assertTrue(isinstance(df1.__repr__(), str))
