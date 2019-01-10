from lemuras import Table
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 1, 12, '+79360360193'],
	['B', 4, 12, 84505505151],
	['A', 3, 10, '+31415926535'],
	['B', 6, 14, ''],
	['A', 4, 10, '23816326412'],
	['A', 2, 12, 0],
]
agg_rule = { 'size': { 'Count': len, 'Value': lambda x: sum(x)*3, 'Any': 'last' } }


class TestLemurasGroupby(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(TestLemurasGroupby, self).__init__(*args, **kwargs)
		self.df1 = Table(cols, rows)
		self.gr = self.df1.groupby(['type', 'weight'])

	def test_groups(self):
		dfc = self.gr.counts()
		self.assertEqual(dfc.rowcnt, 4)
		self.assertEqual(set(dfc.columns), {'type', 'weight', 'rows'})
		self.assertEqual(dfc['weight'].sum(), 48)
		self.assertEqual(dfc['rows'].sum(), 6)
		part = self.gr.get_group(['A', 12])
		self.assertEqual(set(part.columns), {'type', 'weight', 'size', 'tel'})
		self.assertEqual(part['size'].sum(), 3)
		# TODO: test self.gr.split()

	def test_agg_main(self):
		df2 = self.gr.agg(agg_rule)
		self.assertEqual(set(df2.columns), {'type', 'weight', 'Count', 'Value', 'Any'})
		self.assertEqual(df2.rowcnt, 4)
		self.assertEqual(df2['weight'].sum(), 48)
		self.assertEqual(df2['Count'].sum(), 6)
		self.assertEqual(df2['Value'].sum(), 60)

	def test_agg_default(self):
		df2 = self.gr.agg({}, 'first')
		self.assertEqual(set(df2.columns), {'type', 'weight', 'size', 'tel'})
		self.assertEqual(df2.rowcnt, 4)

	def test_by_all(self):
		grall = self.df1.groupby()
		df2 = grall.agg(agg_rule)
		self.assertEqual(set(df2.columns), {'Count', 'Value', 'Any'})
		self.assertEqual(df2.rowcnt, 1)
		self.assertEqual(df2.cell('Count'), 6)
		self.assertEqual(df2.cell('Value'), 60)
