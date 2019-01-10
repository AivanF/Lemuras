from lemuras import Table
import unittest


html_table = """
<table>
	<thead><tr>
		<th>Name</th><th>Value</th>
	</tr></thead>
	<tbody><tr class="odd">
		<td>Pi</td><td>3.1415926535</td>
	</tr><tr class="even">
		<td>Euler</td><td>2.7182818284</td>
	</tr><tr class="odd">
		<td>Phi</td><td>1.6180339887</td>
	</tr></tbody>
</table>
"""


class TestLemurasHtml(unittest.TestCase):
	def test_load(self):
		df1 = Table.from_html(html_table, title='Numbers')
		self.assertEqual(df1.columns, ['Name', 'Value'])
		self.assertEqual(df1.rowcnt, 3)
		self.assertEqual(df1['Value'].sum(), 7.4779084706)

	def test_save(self):
		txt = Table.from_html(html_table).html()
		df2 = Table.from_html(txt, title='Numbers')
		self.assertEqual(df2.columns, ['Name', 'Value'])
		self.assertEqual(df2.rowcnt, 3)
		self.assertEqual(df2['Value'].sum(), 7.4779084706)
