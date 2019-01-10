from lemuras import Table
import unittest


tsv_table = """ID	Name	Date
31415	Aivan	1983-09-14
27182	Fouren	13.08.2018
"""


class TestLemurasCsv(unittest.TestCase):
	def test_load(self):
		df1 = Table.from_csv(tsv_table, title='IDs', inline=True, delimiter='\t')
		self.assertTrue('datetime.date' in str(type(df1.cell('Date', 1))))
		self.assertEqual(df1.columns, ['ID', 'Name', 'Date'])
		self.assertEqual(df1.cell(1, 1), 'Fouren')
		self.assertEqual(df1.rowcnt, 2)
		self.assertEqual(df1['ID'].sum(), 58597)

	def test_save(self):
		df2 = Table.from_csv(Table.from_csv(tsv_table, inline=True, delimiter='\t').to_csv(), title='IDs', inline=True)
		self.assertTrue('datetime.date' in str(type(df2.cell('Date', 1))))
		self.assertEqual(df2.columns, ['ID', 'Name', 'Date'])
		self.assertEqual(df2.cell(1, 1), 'Fouren')
		self.assertEqual(df2.rowcnt, 2)
		self.assertEqual(df2['ID'].sum(), 58597)
