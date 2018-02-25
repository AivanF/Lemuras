# Lemuras

Sometimes you cannot or don't want to use Pandas or similar advanced tool for data analysis, but still have a need to manipulate large tables. In such cases you can use **Lemuras** – it is a *pure Python* library in a single file without dependencies. And if you have some experience of Pandas or SQL, then you can easily work with Lemuras.

Again, this library may be considered as a simplified analogue of Pandas, but not as a replacement. However, Lemuras is capable of processing an operation on a few tables with several thousands of rows in less than a second.

## Features

- Integration with *Jupyter IPython Notebook*: Lemuras objects are printed as nice tables.
- Most of the syntax is very similar to *Pandas*.
- Save / load **CSV files**.
- Cells accessing, columns renaming, rows sorting, functions/lambdas applying.
- Dealing with **columns**: you can take a table column, do math with the values, compare, check existing in other column or list, then filter a table by , etc.
- **Grouping by** *none*, *one*, or *multiple columns*, **aggregation** with *built-in* or *user-defined functions and lambdas*.
- **Merge** (**Join**): *inner / left / right / outer*.
- **Pivot tables** creation.

It was tasted on both Python **2.7.13** and Python **3.6.0**.


## Examples

All the features are described in notebook examples:

1. [Basic things](https://github.com/AivanF/Lemuras/blob/master/Example%201%20-%20Basic%20things.ipynb)
1. [Group by](https://github.com/AivanF/Lemuras/blob/master/Example%202%20-%20Group%20By.ipynb)
1. [Merge / Join](https://github.com/AivanF/Lemuras/blob/master/Example%203%20-%20Merge%20Join.ipynb)
1. [Pivot table](https://github.com/AivanF/Lemuras/blob/master/Example%204%20-%20Pivot%20table.ipynb)

In addition, there is one complex example of solving a real-life problem:

- [Retargeting results report](https://github.com/AivanF/Lemuras/blob/master/Complex%20Example%20-%20Retargeting%20results%20report.ipynb)

The code is well-commented, so, you can find useful information there. Contributions are welcome.


## TODOs

There are some things that are good to be implemented:

- **Tables concatenation**. Like `UNION` in *SQL* or `pd.concat` in *Pandas*.
- **Tables creation by columns**. For now there is no built-in way to add or delete columns, or create a new table with different columns.


## License

 This software is provided 'as-is', without any express or implied warranty.
 You may not hold the author liable.

 Permission is granted to anyone to use this software for any purpose,
 including commercial applications, and to alter it and redistribute it freely,
 subject to the following restrictions:

 The origin of this software must not be misrepresented. You must not claim
 that you wrote the original software. When use the software, you must give
 appropriate credit, provide a link to the original file, and indicate if changes were made.
 This notice may not be removed or altered from any source distribution.
