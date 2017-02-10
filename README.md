

### Feature Generation using Sparse/Dense Query/Document vectors

#### 1. Java codes

Project folder: FeatureGeneration
Main Class: QueryDocFeatureGenerator.java

Command line argument inputs:
 - type of model: 'bm25', 'tfidf', 'doc2vec'
 - address of the directory that contains documents
 - address of a .txt file that contains queries (one query per line)
 - version tag (optional)    

Output:
 -a .tsv file of similarity scores (features) matrix in which rows are 
 the documents and columns are the queries. The name of the output file
 is made by the following pattern: model name + "_features_" +
 version tag (if any) 

External libraries:
 - Lucene
 - DL4J (not implemented yet)


Compilation:
 - cd ./FeatureGeneration
 - mvn package 
Or 
 - javac -cp ... QueryDocFeatureGenerator.java

Execution:
 - java -jar FeatureGeneration-1.0-SNAPSHOT-jar-with-dependencies.jar 'type of model' 'document directory' 'queries file address' 'tag'


*** The doc2vec functionality will be added to this project using DL4j library. The Python scripts and Gensim library in Python are being used for now for calculating Dense (continuous) feature vectors and finding similarity/ranking scores.***

#### 2. Python codes

##### 2.1 Caluclating Similarity Scores using Doc2Vec model.

Script name: dataFeatureGeneration_SupportSearch_Doc2VecModel.py

Command line argument inputs:
 - Address of the titles directory
 - Address of the summaries directory
 - Address of the bodies directory
 - Address of query-url .tsv file
 - Address of the trained Doc2Vec model
 - Address of a previosuly calculated query-url scores in the same schema as output (Optional)

Output:
 - A .tsv file in the folllwing schema:
    query | url | titles scores | summaries scores | bodies scores


External libraries:
- Pandas
- Numpy
- Support_final


##### 2.2 Data Processing

The following scripts are used for processing/preparing documents
    
 - extractTextXml.py: is used for extracting data from .xml support data. Uses xmlTextExtractor class in Support_final 

  - inputs:
   - Director that contains folders of Support data documents (e.g., DL, HT, TA, ...)
    - Address of a drectory to move threads files to (DI)
    - Address of a directory to move documents files to.
    
  - output:
   - three .txt documents that contain extracted documents from threads, documents, and combined.


 - titleBodySummaryDirectoryBuilder.py: Uses generated files by the previous script to make three separate directories for titles, summaries, and bodies texts. The names of the files in all three directories are the same (urls).

  - inputs:
   - Extracted threads address
   - Extracted documents address
   - Address of a directory to create document folders
  
  - outputs: three directories names titles, summaries, and bodies documents.



  






