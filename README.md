

Feature Generation Workflow:
---
---

Scraping title, body, summary text from support corpus:

```python 

python ./SearchProject/Class/extractText.py --help

usage: Reads and parses support documents. [-h] [--dataFormat DATAFORMAT]
[--tempDir TEMPDIR]
[--threadsDestFile THREADSDESTFILE]
[--docsDestFile DOCSDESTFILE]
[--allData ALLDATA]
[--filterData FILTERDATA]
rawDataDir

positional arguments:
rawDataDir            Address of a directory that ontains the following
folders of extracted data from apple .com in .xml or
.json formats: 'DI' (for threads), and 'DL', 'HT',
'MA', 'PH', 'PK', 'SP', 'TA', 'TS' for documents.

optional arguments:
-h, --help            show this help message and exit
--dataFormat DATAFORMAT, -dataFormat DATAFORMAT
Format of data in the folders, input either json or
xml
--tempDir TEMPDIR, -tempDir TEMPDIR
Temporary directory for copying documents and threads
in separate folders. Used by xmlscrappers.py
--threadsDestFile THREADSDESTFILE, -threadsDestFile THREADSDESTFILE
Address of final file that contains all scrapped
threads text
--docsDestFile DOCSDESTFILE, -docsDestFile DOCSDESTFILE
Address of final file that contains all scrapped
documents text
--allData ALLDATA, -allData ALLDATA
Address of final file that contains all scrapped text
--filterData FILTERDATA, -filterData FILTERDATA
Determines Whether the extracted data should be
filtered or not

```

The outputs are used by the next module to generate docuemnts directory for indexing and feature generation. 

***



