from lemuras import Table
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 1, 10, '+79360360193'],
	['B', 4, 12, 84505505151],
]
df1 = Table(cols, rows, 'First')

cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 2, 10, '31415926535'],
	['B', 6, 14, ''],
	['A', 3, 12, 0],
]
df2 = Table(cols, rows, 'Second')


class TestLemurasConcat(unittest.TestCase):
	def test_concat(self):
		df3 = Table.concat([df1, df2])
		self.assertEqual(df1.columns, df3.columns)
		self.assertEqual(df3.rowcnt, df1.rowcnt+df2.rowcnt)
		self.assertEqual(df3['size'].sum(), df1['size'].sum()+df2['size'].sum())

		df1.append(df2)
		# Now, df1 must be equal to df3
		self.assertEqual(df1.columns, df2.columns)
		self.assertEqual(df1.rowcnt, df3.rowcnt)
		self.assertEqual(df1['size'].sum(), df3['size'].sum())

		trash = '1234567890'
		df3.rows[1][3] = trash
		df3.rows[4][3] = trash
		# It must not affect df1 or df2
		self.assertEqual((df1['tel']==trash).sum(), 0)
		self.assertEqual((df2['tel']==trash).sum(), 0)
		self.assertEqual((df3['tel']==trash).sum(), 2)
