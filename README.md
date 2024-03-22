# eri-csv-item-split
Single-use script in Python to split CSV column with varying syntax.
Example of input CSV is included.

How to use:

1. Download from Google Sheet as a TSV (tab separated values)
2. Column headings should include `id` and `Nutri` - other columns will be ignored.
3. Item delimiter should be tabulator, each item should be on exacltly one line.
4. Convert then to Windows 1250/CP1250 (ANSI) encoding.
5. Use the script to parse data (input filename and path are written in the beginning of the script.