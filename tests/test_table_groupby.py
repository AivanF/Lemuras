import unittest
from lemuras import Table
from .sample_data import cols, rows, df1

agg_rule = { 'size': { 'Count': len, 'Value': lambda x: sum(x)*3, 'Any': 'last' } }


class TestLemurasTableGroupby(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(TestLemurasTableGroupby, self).__init__(*args, **kwargs)
		df1 = Table(cols, rows)
		self.gr = df1.groupby(['type', 'weight'])

	def test_groups(self):
		dfc = self.gr.counts()
		self.assertEqual(dfc.rowcnt, 5)
		self.assertEqual(set(dfc.columns), {'type', 'weight', 'rows'})
		self.assertEqual(dfc['weight'].sum(), 63)
		self.assertEqual(dfc['rows'].sum(), 6)
		
		part = self.gr.get_group(['A', 12])
		self.assertEqual(set(part.columns), set(df1.columns))
		self.assertEqual(part['size'].sum(), 3)
		
		part = self.gr.get_group(['A', 123])
		self.assertEqual(part, None)

	def test_split(self):
		gr = df1.groupby('type')
		dfc = gr.counts()

		res = gr.split(pairs=True, add_keys=False)
		self.assertEqual(len(res), dfc.rowcnt)
		for pair in res:
			keys = pair[0]
			tbl = pair[1]
			self.assertEqual(tbl.colcnt, df1.colcnt-1)
			self.assertEqual(tbl.rowcnt, dfc.find(keys)['rows'])
		
		res = gr.split(pairs=True, add_keys=True)
		self.assertEqual(len(res), dfc.rowcnt)
		for pair in res:
			keys = pair[0]
			tbl = pair[1]
			self.assertEqual(tbl.colcnt, df1.colcnt)
			self.assertEqual(tbl.rowcnt, dfc.find(keys)['rows'])

	def test_agg_main(self):
		df2 = self.gr.agg(agg_rule)
		self.assertEqual(set(df2.columns), {'type', 'weight', 'Count', 'Value', 'Any'})
		self.assertEqual(df2.rowcnt, 5)
		self.assertEqual(df2['weight'].sum(), 63)
		self.assertEqual(df2['Count'].sum(), 6)
		self.assertEqual(df2['Value'].sum(), 60)

	def test_agg_default(self):
		df2 = self.gr.agg({}, 'first')
		self.assertEqual(set(df2.columns), set(df1.columns))
		self.assertEqual(df2.rowcnt, 5)

		# Default functions in a list must be string names
		with self.assertRaises(ValueError) as context:
			x = self.gr.agg({}, [min, max])
		self.assertTrue('str' in str(context.exception))

		# Aggregation function must be a callable
		with self.assertRaises(ValueError) as context:
			x = self.gr.agg({}, {'some':{'pi':3.14}})
		self.assertTrue('callable' in str(context.exception))

	def test_by_one(self):
		gr = df1.groupby('type')
		df2 = gr.agg(agg_rule)
		self.assertEqual(set(df2.columns), {'type', 'Count', 'Value', 'Any'})
		self.assertEqual(df2.rowcnt, df1['type'].nunique())
		self.assertEqual(df2['Count'].avg(), df1.rowcnt/df2.rowcnt)

	def test_by_all(self):
		grall = df1.groupby()
		df2 = grall.agg(agg_rule)
		self.assertEqual(set(df2.columns), {'Count', 'Value', 'Any'})
		self.assertEqual(df2.rowcnt, 1)
		self.assertEqual(df2.cell('Count'), 6)
		self.assertEqual(df2.cell('Value'), 60)

	def test_repr(self):
		self.assertTrue(isinstance(self.gr.__repr__(), str))
		self.assertTrue(isinstance(self.gr._repr_html_(), str))
