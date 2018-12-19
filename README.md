# Lemuras

Sometimes you cannot or don't want to use Pandas or similar advanced tool for data analysis, but still have a need to manipulate large tables with code. In such cases you can use **Lemuras** – it is a *pure Python* library without external dependencies. And if you have some experience of Pandas or SQL, then you can easily work with Lemuras.

Again, this library may be considered as a simplified analogue of Pandas, but not as a replacement. However, Lemuras is capable of processing an operation on a few tables with several thousands of rows in less than a second on a simple web server. So, if you need a tiny library to generate analytical reports or convert table formats, Lemuras is a good choice!

![logo](http://www.aivanf.com/static/cv/lemuras.png)

## Features

- Integration with *Jupyter IPython Notebook*: Lemuras objects are printed as nice tables.
- Save / load **CSV files**, **JSON**, **HTML** tables, **SQL** (both query result and table creation code).
- Automatic columns types detection, simple type conversion.
- Cells access, rows, columns adding, deleting, columns renaming, functions/lambdas applying, rows sorting.
- Advanced processing of **columns**: you can take any table column, apply any function or lambda, do math with several columns and discrete values, compare them, check existing in other columns or lists, filter a table by it or add it to a table, etc... In other words, you can do anything!
- **Grouping by** *none*, *one*, or *multiple columns*, **aggregation** with *built-in* or *user-defined functions and lambdas* for specified or just all the columns.
- **Merge** (**Join**): *inner / left / right / outer*.
- **Tables concatenation** and **appending**.
- **Pivot tables** creation.

It was tasted on both Python **2.7** and Python **3.6**


## Installation 

There are 2 simple options:

- Use `pip install Lemuras` [(view project on PyPI)](https://pypi.org/project/Lemuras/).

- Copy `lemuras` folder [from GitHub](https://github.com/AivanF/Lemuras) if you want the freshest version.


## Examples

All the features are described in notebook examples:

1. [Basic things](https://github.com/AivanF/Lemuras/blob/master/examples/Example%201%20-%20Basic%20things.ipynb) – access to columns, cells, rows; add, delete, change their values; also filtering and sorting.
1. [Group by](https://github.com/AivanF/Lemuras/blob/master/examples/Example%202%20-%20Group%20By.ipynb) – grouping and combining (aggregating).
1. [Merge / Join](https://github.com/AivanF/Lemuras/blob/master/examples/Example%203%20-%20Merge%20Join.ipynb) – such types: inner, outer, left, right.
1. [Pivot table](https://github.com/AivanF/Lemuras/blob/master/examples/Example%204%20-%20Pivot%20table.ipynb) – create new tables with columns, rows and cells from another table.
1. [Tables Concatenate / Append](https://github.com/AivanF/Lemuras/blob/master/examples/Example%205%20-%20Tables%20Concatenate%20Append.ipynb) – simple tables concatenation and appending.
1. [Types, Read/Write, CSV, SQL, JSON, HTML](https://github.com/AivanF/Lemuras/blob/master/examples/Example%206%20-%20Types%20Read%20Write%20CSV%20SQL%20JSON%20HTML.ipynb) – description of Lemuras supported data types, saving to and loading from CSV, SQL, JSON, HTML formats.

In addition, there is one complex example of solving a real-life problem:

- [Retargeting results report](https://github.com/AivanF/Lemuras/blob/master/examples/Complex%20Example%20-%20Retargeting%20results%20report.ipynb)

The code of Lemuras is well-commented, so, you can find useful information there. Contributions are welcome.


## ToDos

The list [is available on GitHub](https://github.com/AivanF/Lemuras/issues/1).

## License

 This software is provided 'as-is', without any express or implied warranty.
 You may not hold the author liable.

 Permission is granted to anyone to use this software for any purpose,
 including commercial applications, and to alter it and redistribute it freely,
 subject to the following restrictions:

 The origin of this software must not be misrepresented. You must not claim
 that you wrote the original software. When use the software, you must give
 appropriate credit, provide an active link to the original file, and indicate if changes were made.
 This notice may not be removed or altered from any source distribution.
