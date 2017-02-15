
### Feature Generation using Sparse/Dense Query/Document vectors

##### 1. Data Preprocessing

The Support_final package can be used as explained in the following.

- Data Extraction/preprocessing:
    - filtering:
        - filter class in filters.py module:
        - Removing stop words (myStopWords.list in SourceFiles folder in Support_final package)
            - performing manual mapping for typos and cotractions (e.g., iphon, i've, ...)
            This step uses the mapping WordsStemManual.txt file in the SourceFiles directory
            - Performing Lematization (nouns and verbs)
            - Removing stop words (again, since some words may be as stop words after manual change)
            - Removing "'s"
            - Removing quotation marks ([\'\"])
            - Removing URLs: ("(?P<url>https?://[^\s]+)")
            - Replacing punctuations ("?", "!") with "." (period is kept since it is being used to separate 
            sentences
            - Replacing the [non-alpha numeric and space] (([^a-zA-Z0-9\s]+) with space
            - lower casing and stripping

    - Data extraction:
        - XmlTextExtractor class in xmlscrappers.py can be used. This class uses 
        the filters module to clean the text. The tex processing steps taken are as the following:
        
    - model training:
    
    Doc2Vec model training:
        - can be done through Support_final:
       Example: 
       
    ``` python
    
    Required arguments: trainingDataAddress, tagSeparator (delimiter that separates dic ids and sentences)
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
    
    Trained model will be saved inside Support_instance. To save: Support_isntance.modelClass.model.save("destAddress")





