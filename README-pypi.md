# Lemuras

Sometimes you cannot or don't want to use Pandas or similar advanced tool for data analysis, but still have a need to manipulate large tables with code. In such cases you can use **Lemuras** – it is a *pure Python* library without external dependencies. And if you have some experience of Pandas or SQL, then you can easily work with Lemuras.

Again, this library may be considered as a simplified analogue of Pandas, but not as a replacement. However, Lemuras is capable of processing an operation on a few tables with several thousands of rows in less than a second on a simple web server. So, if you need a tiny library to generate analytical reports or convert table formats, Lemuras is a good choice!

## Features

- Integration with *Jupyter IPython Notebook*: Lemuras objects are printed as nice tables.
- Save / load **CSV files**, **JSON**, **HTML** tables, **SQL** (both query result and table creation code).
- Automatic columns types detection, simple type conversion.
- Access, add, edit, delete cells, rows, columns. Apply custom of built-in functions, lambdas, sort the data, iterate over rows.
- Advanced processing of **columns**: you can take any table column, apply any function or lambda, do math with several columns and discrete values, compare them, check existing in other columns or lists, filter a table by it, or add it to a table, etc... In other words, you can do anything!
- **Grouping by** *none*, *one*, or *multiple columns*, **aggregation** with *built-in* or *user-defined functions and lambdas* for specified or just all the columns.
- **Merge** (**Join**): *inner / left / right / outer*.
- **Tables concatenation** and **appending**.
- **Pivot tables** creation.

It was tasted on both Python **2.7** and Python **3.6**

## Examples

All the features are described in notebook examples:

1) [Basic things](https://github.com/AivanF/Lemuras/blob/master/examples/Example%201%20-%20Basic%20things.ipynb) – access to columns, cells, rows; add, delete, change their values; also filtering and sorting.
1.5) [Functions applying](https://github.com/AivanF/Lemuras/blob/master/examples/Example%201.5%20-%20Functions%20Applying.ipynb) – apply functions or lambda expressions to columns or tables, change types, aggregate values, use your own or one of lots predefined useful functions (oncluding statistical ones).
2) [Group by](https://github.com/AivanF/Lemuras/blob/master/examples/Example%202%20-%20Group%20By.ipynb) – grouping and combining (aggregating).
3) [Merge / Join](https://github.com/AivanF/Lemuras/blob/master/examples/Example%203%20-%20Merge%20Join.ipynb) – such types: inner, outer, left, right.
4) [Pivot table](https://github.com/AivanF/Lemuras/blob/master/examples/Example%204%20-%20Pivot%20table.ipynb) – create new tables with columns, rows and cells from another table.
5) [Tables Concatenate / Append](https://github.com/AivanF/Lemuras/blob/master/examples/Example%205%20-%20Tables%20Concatenate%20Append.ipynb) – simple tables concatenation and appending.
6) [Types, Read/Write, CSV, SQL, JSON, HTML](https://github.com/AivanF/Lemuras/blob/master/examples/Example%206%20-%20Types%20Read%20Write%20CSV%20SQL%20JSON%20HTML.ipynb) – description of Lemuras supported data types, saving to and loading from CSV, SQL, JSON, HTML formats.

In addition, there are complex examples of solving a real world problems:

- [Retargeting results report](https://github.com/AivanF/Lemuras/blob/master/examples/Complex%20Example%20-%20Retargeting%20results%20report.ipynb)

- [Filtration by location area](https://github.com/AivanF/Lemuras/blob/master/examples/Complex%20Example%202%20-%20Filtering%20by%20Location%20Area.ipynb)

The code of Lemuras is well-commented, also there are many unit-tests, so, you can easily find useful information there. Contributions are welcome.
