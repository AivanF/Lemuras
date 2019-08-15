from datetime import date
import unittest
from lemuras import Table, Column
from .sample_data import cols, rows, df1

cdates = Column(['2018-12-30', '14.09.1983', '02/15/1916'], 'Dates')


class TestLemurasColumns(unittest.TestCase):
	def test_basic(self):
		# Only either values or table (with source_name) must be set
		with self.assertRaises(ValueError) as context:
			x = Column()
		with self.assertRaises(ValueError) as context:
			x = Column(values=[], table=df1, source_name='size')
		with self.assertRaises(ValueError) as context:
			x = Column(table=df1)

		# Setting value
		df2 = df1.copy()
		df2['type'][1] = 'C'
		self.assertEqual(df2['type'].nunique(), df1['type'].nunique() + 1)

		# Nonexistent names must lead to specific error
		# It is important due to __getattr__ overriding
		with self.assertRaises(AttributeError) as context:
			x = df2['size'].random_name

		with self.assertRaises(ValueError) as context:
			x = df2['size'].apply('random_name')
		self.assertTrue('does not exist' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			x = df2['size'].calc('random_name')
		self.assertTrue('does not exist' in str(context.exception))

	def test_compare(self):
		df2 = df1.copy()
		self.assertEqual((df2['weight'] == 12).sum(), 3)
		self.assertEqual((df2['weight'] < 12).sum(), 1)
		self.assertEqual((df2['weight'] > 12).sum(), 2)
		self.assertEqual((df2['weight'] > df2['size']).sum(), 6)

	def test_operators(self):
		df2 = df1.copy()
		# Simple math operations
		self.assertEqual((df2['weight']-df2['size']).sum(), 55)
		self.assertEqual((df2['weight']+df2['size']).sum(), 95)
		self.assertEqual((df2['weight']*df2['size']).sum(), 258)
		nega = df2['weight'] - df2['size'] * 10
		self.assertTrue(nega.sum() < 0)
		self.assertTrue(abs(nega).sum() > 0)
		# Multiply by a float one because in Python 2 division doesn't convert int to float
		self.assertEqual((df2['weight']*1.0/df2['size']).avg(), 5.069444444444444)
		# Logical operations & comparison
		self.assertEqual(((df2['weight'] < 12)|(df2['weight'] > 12)).sum(), 3)
		self.assertEqual(((df2['weight'] <= 12)&(df2['weight'] == 12)).sum(), (df2['weight'] == 12).sum())
		self.assertEqual((~(df2['weight'] <= 12)).sum(), 2)
		# Different lengths
		with self.assertRaises(ValueError) as context:
			x = df1['weight'] + [1, 3, 2]
		# Contains operator
		self.assertFalse(123 in df1['size'])
		self.assertTrue(4 in df1['size'])

	def test_agg(self):
		df2 = df1.copy()
		self.assertEqual(df2['weight'].avg(), 12.5)
		self.assertEqual(df2['weight'].std(), 1.6072751268321592)
		self.assertEqual(df2['weight'].q1(), 12.0)
		self.assertEqual(df2['weight'].median(), 12.0)
		self.assertEqual(df2['weight'].q3(), 13.5)
		self.assertEqual(df2['weight'].mode(), 12)
		self.assertEqual(df2['weight'].count(), 6)
		self.assertEqual(df2['weight'].nunique(), 4)
		self.assertEqual(df2['type'].nunique(), 2)
		self.assertEqual(df2['size'].min(), 1)
		self.assertEqual(df2['size'].max(), 6)
		self.assertEqual(df2['size'].first(), 1)
		self.assertEqual(df2['size'].get(0), 1)
		self.assertEqual(df2['size'].last(), 2)
		self.assertEqual(df2['size'].get(-1), 2)
		self.assertEqual(df2['tel'].first(), df2['tel'][0])
		self.assertEqual(df2['tel'].last(), df2['tel'][-1])
		self.assertEqual(df2['tel'].nulls(), df2['tel'].isnull().sum())

		# Percentile function works a bit different for odd and even lengths
		# So, let's test both options
		temp = df2['weight'].copy()
		temp.values.append(df2['weight'].mean())
		self.assertEqual(temp.q2(), df2['weight'].q2())

		empty = Column([], 'Empty')
		# Thanks to @call_with_numbers_only and @call_with_existing_only
		self.assertEqual(empty.avg(), None)
		self.assertEqual(empty.std(), None)
		self.assertEqual(empty.min(), None)
		self.assertEqual(empty.max(), None)

	def test_types(self):
		df2 = df1.copy()
		self.assertEqual(df2['tel'].copy().str().istype(str).sum(), df2.rowcnt)
		self.assertEqual(df2['tel'].copy().int().istype(int).sum(), df2.rowcnt)
		self.assertEqual(df2['tel'].copy().int().avg(), 36516353048.5)
		self.assertEqual(df2['tel'].copy().int(default=None).avg(), 54774529572.75)
		self.assertEqual(df2['tel'].copy().isnull().sum(), 1)
		self.assertEqual(df2['tel'].copy().int().isnull().sum(), 0)
		self.assertEqual(df2['tel'].copy().float().istype(float).sum(), df2.rowcnt)
		self.assertEqual(df2['size'].copy().none_to(0).nulls(), 0)

	def test_apply(self):
		df2 = df1.copy()
		saved = df2['tel'].sum()
		self.assertEqual(df2['tel'].lengths(strings_only=True).sum(), 34)
		self.assertEqual(df2['tel'].lengths(strings_only=False).sum(), 49)
		self.assertEqual(df2['size'].isin([1, 3]).sum(), 2)
		self.assertEqual(cdates.date().istype(date), 3)

		def func(value, a, b):
			return value * b + a 
		self.assertEqual(df2['size'].apply(func, 3, b=2).sum(), df2['size']*2+df2.rowcnt*3)

		# Must be not changed
		self.assertEqual(df2['tel'].sum(), saved)

	def test_folds(self):
		folds = df1['weight'].folds(3)
		agg_sum = 0
		agg_cnt = 0
		for cur in folds:
			agg_sum += cur.sum()
			agg_cnt += cur.rowcnt
		self.assertEqual(agg_sum, df1['weight'].sum())
		self.assertEqual(agg_cnt, df1.rowcnt)

		self.assertEqual(df1['weight'].folds(1)[0], df1['weight'])

	def test_table(self):
		df2 = df1.copy()
		df2.int()
		self.assertEqual(df2['type'].min(), 0)
		self.assertEqual(df2['type'].max(), 0)
		self.assertEqual(df1['type'].min(), 'A')
		self.assertEqual(df1['type'].max(), 'B')

	def test_loc(self):
		a = Column([1,3,5,7], title='cA')
		b = Column([1,2,3], title='cB')

		# Wrong type
		with self.assertRaises(ValueError) as context:
			a.loc({3, 1, 4})

		# Wrong length
		with self.assertRaises(ValueError) as context:
			a.loc(b.isin(a))

		# Similar to Column(set(a)-set(b))
		# but saves values order
		res = a.loc(~a.isin(b))
		self.assertTrue(set(res) == {5,7})

	def test_repr(self):
		temp = Column(list(df1[0].get_values()) + list(df1[1].get_values()) + list(df1[2].get_values()))
		self.assertTrue(temp.rowcnt > 10)
		self.assertTrue(isinstance(temp._repr_html_(), str))
		self.assertTrue(isinstance(temp.__repr__(), str))
