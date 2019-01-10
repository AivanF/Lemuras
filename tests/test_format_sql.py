from lemuras import Table
import unittest


cols = ['type', 'size', 'weight', 'tel']
rows = [
	['A', 1, 12, '+79360360193'],
	['B', 4, 12, 84505505151],
	['A', 3, 10, '31415926535'],
	['B', 6, 14, ''],
	['A', 4, 15, '23816326412'],
	['A', 2, 11, 0],
]

sql_result = """+------+--------------+--------+--------+--------+
| id   | name         | q1     | q2     | q3     |
+------+--------------+--------+--------+--------+
| 1005 | ABC          |   3286 |     10 |     14 |
| 1006 | DEF          |    800 |     19 |     19 |
| 1010 | ghi          |   5140 |     18 |      3 |
| 2000 | gkl          |  18067 |  90817 |  61933 |
| 2004 | mnp          |  47150 | 215139 | 170291 |
| 4046 | oqr          |   6856 |  17665 |  12808 |
| 4048 | stu          |   1765 |   4176 |   2385 |
| 4050 | vxyz         |   2158 |  16577 |  11725 |
+------+--------------+--------+--------+--------+"""


class TestLemurasSql(unittest.TestCase):
	def test_queries(self):
		df1 = Table(cols, rows, 'Sample')
		q_create = df1.to_sql_create()
		q_values = df1.to_sql_values()

		df2 = Table.from_sql_create(q_create)
		df2.add_sql_values(q_values)

		self.assertEqual(df1.columns, df2.columns)
		self.assertEqual(df1.rowcnt, df2.rowcnt)
		self.assertEqual(df1['size'].sum(), df2['size'].sum())
		self.assertEqual(df1['weight'].sum(), df2['weight'].sum())

	def test_load_results(self):
		df2 = Table.from_sql_result(sql_result)
		self.assertEqual(df2.columns, ['id', 'name', 'q1', 'q2', 'q3'])
		self.assertEqual(df2.rowcnt, 8)
		self.assertEqual(df2['id'].sum(), 19169)
