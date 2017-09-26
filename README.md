

Feature Generation Workflow:
---
---

Scraping title, body, summary text from support corpus:

```

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

Using scraped data for making separate directories for titles, bodies, and summaries for each document/url.

```
python SearchProject/Class/titleBodySummaryDirectoryBuilder.py --help

usage: Prepares  three folders (titles, summaries, and bodies) for indexing and 
finding similarity scores between queries and documents/urls.
       [-h] [-docsDir DOCSDIR] extrThrds extrDocs

positional arguments:
  extrThrds             Address of a file that contains extracted data from
                        threads files. For information about the format,
                        please check xmlscrappers.py in Support Python package
  extrDocs              Address of a file that contains extracted data from
                        documents files. For information about the format,
                        please check xmlscrappers.py in Support Python package

optional arguments:
  -h, --help            show this help message and exit
  -docsDir DOCSDIR, --docsDir DOCSDIR
                        Address of the directory that will contain separated
                        titles, summaries, bodies per document
```

Uses two generated files for documents and threads from previous step, and generates a directory with three folders: titles, summaries, bodies containing data for each document/url named by the documet ID.

***

Generating BM25 and TFIDF scores for pairs of query and documents.

```
python featureGeneration_WordNGrams.py --help
('\n', '----------------------------------------------------------------------------------------------------')
usage: featureGeneration_WordNGrams.py [-h] [-corpusAddress CORPUSADDRESS]
                                       [-tag TAG] [-stream STREAM]
                                       [-minWordCount MINWORDCOUNT]
                                       [-dest DEST] [-saveCorpus SAVECORPUS]
                                       [-corpusAddToSave CORPUSADDTOSAVE]
                                       [-cleanText CLEANTEXT]
                                       documentDir queryUrlAddress N

Generates query-document pairs similarity feature (scores) using the TFIDF and
BM25 models (for n-Grams).

positional arguments:
  documentDir           Address of the directory that holds documents
  queryUrlAddress       Address of a .tsv file that holds query-url data
  N                     Numer indication intended n-Gram, e.g., 1 for unigram,
                        2 for bigram, etc.,

optional arguments:
  -h, --help            show this help message and exit
  -corpusAddress CORPUSADDRESS, --corpusAddress CORPUSADDRESS
                        Address of a previously built corpus/dictionary in
                        pickle format
  -tag TAG, --tag TAG   Tag used for tagging output file name
  -stream STREAM, --stream STREAM
                        Indicating whether produce outputs without using
                        memory (for large files) or in memory.
  -minWordCount MINWORDCOUNT, --minWordCount MINWORDCOUNT
                        Lower threshold on count for including words/tokens in
                        the corpus
  -dest DEST, --dest DEST
                        Address of a file for writing final results
  -saveCorpus SAVECORPUS, --saveCorpus SAVECORPUS
                        Indicating whether corpus should be saved for later
                        use or not (default: False)
  -corpusAddToSave CORPUSADDTOSAVE, --corpusAddToSave CORPUSADDTOSAVE
                        Address of file to save corpus made from documents
  -cleanText CLEANTEXT, --cleanText CLEANTEXT
                        indicate whether the text should be cleaned or not
                        (default: True)
```

Uses the generated directoties for indexing and generates bm25/tfidf features for pairs of query-docID's.

***

Generating feature vectords using different embedding models:

```
python featureGeneration_embeddings.py --help
usage: New Symptom Detection - Cleaner/Stat Finder [-h]
                                                   [-preCalculatedFeatures PRECALCULATEDFEATURES]
                                                   queryDocsAddress
                                                   docsPartsDir vecsFilesDir
                                                   modeldir destAddress

positional arguments:
  queryDocsAddress      Address of query document file with at least two first
                        columns as queries and related document.
  docsPartsDir          Address of the directory that contains three folders
                        named as 'title', 'summaries', 'bodies'. All folders
                        should have equal numbers of files related to
                        documents.
  vecsFilesDir          Address of a directory that contains pre-calculated
                        term embeddings. there should be at least one filefor
                        each of the fasttext and glove models, having terms
                        'fasttext'/'glove' in their names. If there are no
                        files for word2vec doc2vec similar files will be
                        produced and saved to this directory using provided
                        pre-trained language models.
  modeldir              Address of a directory that contains pre-trained
                        language (doc2vec/word2vec) models.
  destAddress           Address of a directory that contains pre-trained
                        language (doc2vec/word2vec) models.

optional arguments:
  -h, --help            show this help message and exit
  -preCalculatedFeatures PRECALCULATEDFEATURES, --preCalculatedFeatures PRECALCULATEDFEATURES
                        Address of table of previously calculated features for
                        query document pairs, to be used for faster
                        computation.
                        
```

Calculates features for using embeddings by four different language models, i.e., FastText, Glove, Word2Vec, and Doc2Vec; And for two different distance metrics, i.e., cosine similarity and WMD(EMD) -- for titles, summaries, bodies. Vector embeddings for vocabulary should be calculated before hand and used by the module via vecsFilesDir. The vector file should have the name of the model in its name, e.g., *_fasttext_*.vec. For Doc2Vec and Word2Vec since there is not output like Glove and FastText in the form of "Token\sembeddings" may exist, the pretrained model will be used. 



