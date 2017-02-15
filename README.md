
### Feature Generation using Sparse/Dense Query/Document vectors

##### 1. Data Preprocessing
Doc2Vec model training:

The Support_final package can be used as explained in the following.

- Data Extraction/preprocessing:
    - Data extraction:
        - XmlTextExtractor class in xmlscrappers.py can be used. This class uses 
        the filters module in   

``` python

Example for model training:
supportInstance_ = Support_final.Support(threadsSourceFolder='',
                                         threadsDestFile='',
                                         documentsSourceFolder='',
                                         documentsDestFile='',
                                         allDataFile='',
                                         isModelTrained=False,
                                         modelType='doc2vec',
                                         trainedModelAddress='',
                                         trainedDictAddress='',
                                         trainingData='',
                                         tags='',
                                         isArrayFiltered=False,
                                         trainingDataAddress=‘./address.txt',
                                         tagSeparator=“::-::-::",
                                         contentSeparator=None,
                                         isDataFiltered=False,
                                         isXmlTextExtracted=True)


```                                         





