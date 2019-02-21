from lemuras import Table, Column
from datetime import date
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
		self.assertEqual((df1['weight'] == 12).sum(), 3)
		self.assertEqual((df1['weight'] < 12).sum(), 2)
		self.assertEqual((df1['weight'] > 12).sum(), 1)
		self.assertEqual((df1['weight'] > df1['size']).sum(), 6)

	def test_operators(self):
		# Simple math operations
		self.assertEqual((df1['weight']-df1['size']).sum(), 50)
		self.assertEqual((df1['weight']+df1['size']).sum(), 90)
		self.assertEqual((df1['weight']*df1['size']).sum(), 238)
		# Multiply by a float one because in Python 2 division doesn't convert int to float
		self.assertEqual((df1['weight']*1.0/df1['size']).avg(), 4.861111111111111)
		# Logical operations & comparison
		self.assertEqual(((df1['weight'] < 12)|(df1['weight'] > 12)).sum(), 3)
		self.assertEqual(((df1['weight'] <= 12)&(df1['weight'] == 12)).sum(), (df1['weight'] == 12).sum())
		self.assertEqual((~(df1['weight'] <= 12)).sum(), 1)
		# Different lengths
		with self.assertRaises(ValueError) as context:
			x = df1['weight'] + [1, 3, 2]
		# Contains operator
		self.assertFalse(123 in df1['size'])
		self.assertTrue(4 in df1['size'])

	def test_agg(self):
		self.assertEqual(df1['weight'].avg(), 11.666666666666666)
		self.assertEqual(df1['weight'].std(), 1.3743685418725535)
		self.assertEqual(df1['weight'].q1(), 10.5)
		self.assertEqual(df1['weight'].median(), 12.0)
		self.assertEqual(df1['weight'].q3(), 12.0)
		self.assertEqual(df1['weight'].mode(), 12)
		self.assertEqual(df1['weight'].count(), 6)
		self.assertEqual(df1['weight'].nunique(), 3)
		self.assertEqual(df1['type'].nunique(), 2)
		self.assertEqual(df1['size'].min(), 1)
		self.assertEqual(df1['size'].max(), 6)
		self.assertEqual(df1['size'].first(), 1)
		self.assertEqual(df1['size'].last(), 2)
		self.assertEqual(df1['tel'].first(), None)
		self.assertEqual(df1['tel'].last(), 0)

	def test_types(self):
		self.assertEqual(df1['tel'].copy().int().avg(), 23289626349.666668)
		self.assertEqual(df1['tel'].copy().int(default=None).avg(), 34934439524.5)
		self.assertEqual(df1['tel'].copy().isnull().sum(), 1)
		self.assertEqual(df1['tel'].copy().int().isnull().sum(), 0)
		self.assertEqual(df1['tel'].copy().lengths(strings_only=True).sum(), 23)
		self.assertEqual(df1['tel'].copy().lengths(strings_only=False).sum(), 39)
		self.assertEqual(df1['size'].copy().isin([1, 3]).sum(), 2)
		self.assertEqual(cdates.date().istype(date), 3)

	def test_folds(self):
		folds = df1['weight'].folds(3)
		agg_sum = 0
		agg_cnt = 0
		for cur in folds:
			agg_sum += cur.sum()
			agg_cnt += cur.rowcnt
		self.assertEqual(agg_sum, df1['weight'].sum())
		self.assertEqual(agg_cnt, df1.rowcnt)

	def test_table(self):
		df2 = df1.copy()
		df2.int()
		self.assertEqual(df2['type'].min(), 0)
		self.assertEqual(df2['type'].max(), 0)
		self.assertEqual(df1['type'].min(), 'A')
		self.assertEqual(df1['type'].max(), 'B')

	def test_repr(self):
		self.assertTrue(isinstance(df1[0]._repr_html_(), str))
		self.assertTrue(isinstance(df1[1].__repr__(), str))
