

## Search Ranking Project 

### Data Extraction and Feature Generation

#### 1. Data EXtraction

- _<span style="color: blue;"> `extractText.py` </span>_

Extracts data from raw support data in .json or .xml formats, and saves them in three separate text files, for threads, documents, and combined.

```bash
Python eliyarasgarieh$ python extractText.py --help
usage: Reads and parses support documents. [-h] [--dataFormat DATAFORMAT]
                                           [--tempDir TEMPDIR]
                                           [--threadsDestFile THREADSDESTFILE]
                                           [--docsDestFile DOCSDESTFILE]
                                           [--allData ALLDATA]
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

```

---


- _<span style="color: blue;"> `titleBodySummaryDirectoryBuilder.py` </span>_

Builds three file for each documnet/url for titles, summaries, and bodies and save them in three separate folders (titles, summaries, bodies) for later use by the feature generation pipeline.
```
Python eliyarasgarieh$ python titleBodySummaryDirectoryBuilder.py --help
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

---

- _<span style="color: blue;"> `trainingDataFromExtracted.py` </span>_

Prepares training data from extracted text data for training language models.

```
Python eliyarasgarieh$ python trainingDataFromExtracted.py --help
usage: Prepares data for training language models. [-h]
                                                   [--outputDir OUTPUTDIR]
                                                   [--labelSep LABELSEP]
                                                   [--labeledDest LABELEDDEST]
                                                   [--unlabeledDest UNLABELEDDEST]
                                                   extrThrds extrDocs

positional arguments:
  extrThrds             Address of a file that contains extracted data from
                        threads files. For information about the format,
                        please check xmlscrappers.py in Support Python package
  extrDocs              Address of a file that contains extracted data from
                        documents files. For information about the format,
                        please check xmlscrappers.py in Support Python package

optional arguments:
  -h, --help            show this help message and exit
  --outputDir OUTPUTDIR, -outputDir OUTPUTDIR
                        Output directory.
  --labelSep LABELSEP, -labelSep LABELSEP
                        Delimiter used for separating labels and text (default
                        is '::') in labeled documents
  --labeledDest LABELEDDEST, -labeledDest LABELEDDEST
                        Address of the prepared labeled data
  --unlabeledDest UNLABELEDDEST, -unlabeledDest UNLABELEDDEST
                        Address of the prepared unlabeled data
```

---

- _<span style="color: blue;"> `corpusBuilder.py` </span>_

Building corpus for each of titles, summaries, bodies (and n-grams) separately for more efficient feature generation process.

```
Python eliyarasgarieh$ python corpusBuilder.py --help
usage: corpusBuilder.py [-h] [-minWordCount MINWORDCOUNT] [-dest DEST]
                        [-cleanText CLEANTEXT]
                        documentsDir N

builds corpus for the titles, summaries, bodies folders in the for different
n-grams,

positional arguments:
  documentsDir          Address of the directory that holds folders of
                        documents (titles, summaries, bodies)
  N                     Numer indication intended n-Gram, e.g., 1 for unigram,
                        2 for bigram, etc.,

optional arguments:
  -h, --help            show this help message and exit
  -minWordCount MINWORDCOUNT, --minWordCount MINWORDCOUNT
                        Lower threshold on count for including words/tokens in
                        the corpus
  -dest DEST, --dest DEST
                        Address of a file for writing final results
  -cleanText CLEANTEXT, --cleanText CLEANTEXT
                        indicate whether the text should be cleaned or not
                        (default: True)

```

---

- _<span style="color: blue;"> `dataFeatureGeneration_SupportSearch_WordNGrams.py` </span>_

Generates (tfidf, bm25) n-gram features for a given set of query-url's. 

```
Python eliyarasgarieh$ python dataFeatureGeneration_SupportSearch_WordNGrams.py --help

 ----------------------------------------------------------------------------------------------------
usage: dataFeatureGeneration_SupportSearch_WordNGrams.py [-h]
                                                         [-corpusAddress CORPUSADDRESS]
                                                         [-tag TAG]
                                                         [-stream STREAM]
                                                         [-minWordCount MINWORDCOUNT]
                                                         [-dest DEST]
                                                         [-saveCorpus SAVECORPUS]
                                                         [-corpusAddToSave CORPUSADDTOSAVE]
                                                         [-cleanText CLEANTEXT]
                                                         documentDir
                                                         queryUrlAddress N

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


---

- _<span style="color: blue;"> `dataFeatureGeneration_SupportSearch_Doc2VecModel.py` </span>_

Generates features using trained Doc2Vec model for a given set of query-url's. 

```
Python eliyarasgarieh$ python dataFeatureGeneration_SupportSearch_Doc2VecModel.py --help

 ----------------------------------------------------------------------------------------------------
usage: Generates query-document pairs similarity feature (scores) using the doc2vecvectors
       [-h] [-dest DEST] [-savedScores SAVEDSCORES] docsDir queryDocs model

positional arguments:
  docsDir               Address of the directory that contains three folders
                        named: titles, summaries, bodies
  queryDocs             Address of the query-doc pairs file in .tsv format
  model                 Address of the trained Doc2Vec model.

optional arguments:
  -h, --help            show this help message and exit
  -dest DEST, --dest DEST
                        Final destinations address for saving calculated
                        feature values in .tsv format.
  -savedScores SAVEDSCORES, --savedScores SAVEDSCORES
                        Address of the saved query-document pairs scores in
                        .tsv format
```

---

- _<span style="color: blue;"> `main.py` </span>_

Runs all the feature generation pipeline and saving the results in proper format for next parts of pipeline.

```
Python eliyarasgarieh$ python main.py --help

 ----------------------------------------------------------------------------------------------------

 ----------------------------------------------------------------------------------------------------
usage: main.py [-h] [-pipelinesDir PIPELINESDIR] [-inputsDir INPUTSDIR]
               [-outputsDir OUTPUTSDIR]
               [-hasDoc2VecFeaturesHsitory HASDOC2VECFEATURESHSITORY]
               [-hasSavedCorpus HASSAVEDCORPUS] [-stream STREAM]
               [-minWordCount MINWORDCOUNT] [-saveCorpus SAVECORPUS]
               [-cleanText CLEANTEXT]
               docsDir queryUrlAddress N config

main module for running feature extraction pipelines and preparing final
results

positional arguments:
  docsDir               Address of the directory that holds documents
  queryUrlAddress       Address of a .tsv file that holds query-url data
  N                     Number indicates intended n-Gram, e.g., 1 for unigram,
                        2 for bigram, etc., (n-gram)
  config                Address of the config file for completing command line
                        arguments (required)

optional arguments:
  -h, --help            show this help message and exit
  -pipelinesDir PIPELINESDIR, --pipelinesDir PIPELINESDIR
                        Address of the directory that includes feature
                        generation pipelines
  -inputsDir INPUTSDIR, --inputsDir INPUTSDIR
                        Address of the directory that includes input files
  -outputsDir OUTPUTSDIR, --outputsDir OUTPUTSDIR
                        Final destinations address/name for saving calculated
                        feature values
  -hasDoc2VecFeaturesHsitory HASDOC2VECFEATURESHSITORY, --hasDoc2VecFeaturesHsitory HASDOC2VECFEATURESHSITORY
                        Indicate whether previously calculated doc2vec
                        features are available.
  -hasSavedCorpus HASSAVEDCORPUS, --hasSavedCorpus HASSAVEDCORPUS
                        Indicate whether previously made corpora are
                        available.
  -stream STREAM, --stream STREAM
                        Indicating whether produce outputs without using
                        memory (for large files) or in memory (n-gram
                        pipeline)
  -minWordCount MINWORDCOUNT, --minWordCount MINWORDCOUNT
                        Lower threshold on count for including words/tokens in
                        the corpus (n-gram pipeline)
  -saveCorpus SAVECORPUS, --saveCorpus SAVECORPUS
                        Indicating whether corpus should be saved for later
                        use or not (n-gram pipeline)
  -cleanText CLEANTEXT, --cleanText CLEANTEXT
                        indicate whether the text should be cleaned or not
                        (n-gram pipeline)
```


---
---

