import unittest
from lemuras import Table
from .sample_data import cols, rows, df1

sql_result = """+------+--------------+--------+--------+--------+
| id   | name         | q1     | q2     | q3     |
+------+--------------+--------+--------+--------+
| 1005 | ABC          |   3286 |   10.7 |     14 |
| 1006 | DEF          |    800 |   19.4 |     19 |
| 1010 | ghi          |   5140 |   18.1 |      3 |
| 2000 | gkl          |  18067 |  908.3 |  61933 |
| 2004 | mnp          |  47150 | 2151.5 | 170291 |
| 4046 | oqr          |   6856 |  176.6 |  12808 |
| 4048 | stu          |   1765 |  417.9 |   2385 |
| 4050 | vxyz         |   2158 | 1657.4 |  11725 |
+------+--------------+--------+--------+--------+"""


class TestLemurasSql(unittest.TestCase):
	def test_queries(self):
		q_create = df1.to_sql_create()
		df1.types = None
		q_values = df1.to_sql_values()

		df2 = Table.from_sql_create(q_create)
		df2.add_sql_values(q_values)

		self.assertEqual(df1.columns, df2.columns)
		self.assertEqual(df1.rowcnt, df2.rowcnt)
		self.assertEqual(df1['size'].sum(), df2['size'].sum())
		self.assertEqual(df1['weight'].sum(), df2['weight'].sum())

	def test_queries_empty(self):
		df0 = Table(cols, [], 'Empty')
		q_create = df0.to_sql_create()
		q_values = df0.to_sql_values()

		df2 = Table.from_sql_create(q_create)
		df2.add_sql_values(q_values)

		self.assertEqual(df1.columns, df2.columns)
		self.assertEqual(df2.rowcnt, 0)

	def test_load_results(self):
		df2 = Table.from_sql_result(sql_result)
		self.assertEqual(df2.columns, ['id', 'name', 'q1', 'q2', 'q3'])
		self.assertEqual(df2.rowcnt, 8)
		self.assertEqual(df2['id'].sum(), 19169)
