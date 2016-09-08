# Final Report

#### Eliyar Asgarieh 
##### September 1, 2016

***
***

## Summary

The following report is prepared for presenting my contribution to the CG project in organized form as well as facilitating the next contributions to the project. The works are first represented in chronological order for better understanding the evolution of the works in the project. The latest versions of the codes are represented at the end of the report. So, the hasty reader may want to just skip to the [final section](#end). In the following, the date headers in bullet points indicate when the works or final results are presented. 

***
### **Initial Studies on the Dictionary and the Log Data**

The research began by studying the existing symptoms and classifications - Affected Product, Component, and Case Issue (PCI) - in the dictionary and their distributions under each clicked/typed symptom/classification categories. The following bullet points summarizes the works and results during this stage. 

* [**_March 3_**] (./sourceFiles/March3): the distribution of CTR and impression metrics prepared by the HyunJoon for the dictionary symptoms were studied and the results were shared.

* [**_March 7_**](./sourceFiles/March7): the outline of the project based on the initial brain storming on the project’s road plan were represented in the CG meeting. The gist of the initial ideas was:
    - Clustering symptoms in separate defined clusters.
    - Ranking PCIs under each cluster based on the extractable information from the dictionary such as their frequency.
    - Comparing the incoming query with symptoms clusters and finding the cluster with highest aggregate similarity.
    - Suggesting the highest ranked classifications.

* [**_March 15_**](./sourceFiles/March15): the following were tasks done for this date.
    - The performance of the current suggestion system was initially investigated (using the statistics prepared by the HyunJooon)
    - The frequency of the symptoms and affected products per product group were initially investigated.
    - The results were presented by using prepared interactive presentation slides during CG meeting.

* [**_March 22_**](./sourceFiles/March22): the following were tasks done for this date.
    - The dictionary was studied in more detail to better understand the diversity of classifications (especially CIs) inside groups defined by symptoms and (eligible) product groups. It was shown that while there can be many cases for which there are less than 3 classifications, but the numbers of cases with high numbers of classifications are still very considerable. (It should be mentioned that this study was made before dictionary expansion, and by expanding the dictionary as well as adding new data to the dictionary, the results can be much more diverse and numbers of classifications under each category after symptom selection will be higher).
    - The work on finding reliable NLP model started by training Doc2Vec models using different data sources. The models were trained by text from the dictionary as well as extracted text from the Support documents shared by Xugang (through HyunJoon). The results of using these trained models for similar symptoms were presented (not assessed quantitatively) during meeting.

* [**_March 29_**](./sourceFiles/March29): the work on the log data was started. Initial statistics coverage and CTR were calculated. Also, the pattern in symptom/classification suggestions and clicks were initially studied. The results were presented during the CG meeting. _The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered_.

* [**_April 5_**](./sourceFiles/April5): the work on the log data was continued. The distribution of symptom suggestions and typing-clicking patterns per PC as well as agent groups were studied. It was shown that some PC groups attract more symptom suggestions. Another part of this study was on the agent’s behavior. It was illustrated that some agents are more into typing habits than the others. _The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered_.	

* [**_April 12_**](./sourceFiles/April12): the work on the log data was continued. The distribution of symptom suggestions and typing-clicking patterns per PC as well as agent groups were studied. It was shown that some PC groups attract more symptom suggestions. Another part of this study was on the agent’s behavior. It was illustrated that some agents are more into typing habits than the others. _The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered_.

* [**_April 21_**](./sourceFiles/April21): The distribution of symptoms-classifications pairs based on the defined clicked-or-typed categories were studied using the updated log data. It was shown that the majority of the data fell into the typed symptom-typed classification category. Also, it was shown that there are cases in which final correct classification was suggested but it was not clicked by the agents. The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered.

***
### Starting Work on the CG Project Pipeline
The following works on the project has more organized and purposeful form after the initial exploratory and try and error phase. The following lines summarize the performed research and achievements during this stage. 

* [**_May 3_**](./sourceFiles/May3): The following bullets summarizes the collection of tasks performed between April 21 and May3. 
 The research was reorganized and a presentation were prepared to summarize the problem, involved challenges, applicable methodologies, and the base pipeline considered for the project at that time. 
    - The relationship between eligible and affected products as well as product groups were briefly studied by bi-partite graphs. It was shown that some product (groups) such as iCloud and iTunes are attracting considerably more eligible products. 
    - The Doc2Vec model from the “genism” library in Python were trained using the extracted data from the log as well as the dictionary for vectorization.
    - Python Packages were written for CG and Support projects. These packages (especially Support package) are extensively used during the project for data extraction/cleaning and model training as well as prediction purposes. 
    - An initial classification machine learning model based on the information from the log and dictionary were designed and implemented in the CG package. This model is not tested and used yet (August 16). 

* [**_May 10_**](./sourceFiles/May10): Connecting of rows of the log was confusing and calculating unique metrics from data proved to be tricky. The extracted data from the log by HyunJoon was used for calculating metrics and studying the log during this week (May 3-9). The codes written during this week can be used on the log data extracted by the HyunJoon. Later on, newer versions of codes were written for comprehensive data extraction using raw log data.

* [**_May 24_**](./sourceFiles/May24): Comprehensive and accurate codes were written in Python for extracting extensive ranges of information and metrics from the raw log data. These codes (with limited updates) are used through the project for weekly analysis of log data. The codes extract data based on both last S, last C, last I pattern and separate SC-CF patterns for each test ID. The comprehensive information extracted using these codes can be found in the report prepared for the meeting held on this date. It was clear from the metrics that the coverage for symptom/classification suggestions are very low.    

* [**_May 31_**](./sourceFiles/May31): To increase the coverages, it was decided to expand the symptom-classification dictionary by propagating the Symptoms-Components-Issues for the similar products. The codes were written in Python for dictionary expansion using set of defined product groups.  The results of this expansion were sent to update the applied dictionary in the system. 
    - The other jobs accomplished during this week (continued from weeks before) was training the Doc2Vec models using extracted data from the support data. The data extraction and model training were done using the modules in the Support package. 

* [**_June 10_**](./sourceFiles/June10): The following bullets summarize the tasks performed during first week of June.
    _ Dictionary symptom clustering: Since many symptoms in the dictionary are suspected to be semantically or syntactically similar, clustering was done on the dictionary symptoms (using the vector presentations of symptoms by the trained Doc2Vec models). The results were sent for expert review. The research on the symptom clustering has been continued in later weeks by trying various vectorization and clustering approaches. 
    _ Other important tasks that started this week and continued through later weeks is writing the new symptom detection (NSD) pipeline. This pipeline has been changed/revised during following weeks (after June 10) for increasing its accuracy and efficiency. 

* [**_June 22_**](./sourceFiles/June22): The following are the tasks performed by this date.
    - The effect of dictionary expansion by propagation and adding SETI symptoms was evaluated. The results were reported to be used by the group for preparing presentation slides (for meeting with managers from other departments). Evaluation the effect of dictionary expansion was very challenging since there was a huge inconsistency between PCI cases (Capital letter, lower case, upper case, etc.) in the log, dictionary, and mapping files. These codes are updated in later weeks for resolving problems related to cases sensitivity. 

* [**_June 17_**](./sourceFiles/July17): The log data extraction codes and dictionary expansion evaluation codes were updated for better quality and performance. The results were communicated with the group, through meeting. 

* [**_July 29_**](./sourceFiles/July29): The idea of keyword expansion for the symptoms were tried. The top tokens in symptoms were selected based on their TFIDF scores, and were expanded using different Word2Vec models by adding similar words to them. In addition, the symptoms were weighted using their CTRs extracted from the log data. This approach were tried and evaluated in the following weeks. 

* [**_Aug 1_**](./sourceFiles/Aug1): The following are the works finished for this date.
    - More work was done on dictionary symptom clustering and codes were refined. The expanded symptoms by the Word2Vec model keywords were used for vectorization and clustering. The results are not very promising, since adding keywords can add noise to the data and make similar symptoms very dissimilar. 
    - The NSD pipeline were revised to be adapted with the Kevin-Saurav’s pipeline for normalizing symptoms.

* [**_Aug 9_**](./sourceFiles/Aug9): Clustering algorithms were tuned using limited available labeled data on the previously prepared clusters. The optimum parameters were obtained to be used for later clustering steps. 

* [**_Aug 12_**](./sourceFiles/Aug12): The idea of increasing symptom coverage by adding n-grams as type-aheads to the data was tried. All combinations of token and letter n-grams were found for symptoms and a data table were prepared for the symptoms in the dictionary. The symptoms were weighted based on their CTR in the log data.

* [**_Aug 17_**](./sourceFiles/Aug17): The effect of n-grams model for symptom coverage were assessed. The results were not very promising since the n-gram model is very restricted on the order of the words. 

* [**_Aug 25_**](./sourceFiles/Aug25): The codes for dictionary expansion by propagation for “Apps” component in iOS devices as well as for “iCloud”, “iTunes”, and “Apple ID” group were written. The symptoms and issues were propagated for groups, and the results were shared through email. Also, the performance of new model called FastText were evaluated.

* [**_Aug 29_**](./sourceFiles/Aug29): The codes for dictionary expansion by propagation were corrected based on the request. The codes were changed to propagate Eligible products (= Affected Products) for all iOS devices that have Apps component (for each symptom and issue); And, the Eligible products for all the “iCloud”, “iTunes”, and “Apple ID” groups (for each symptom, issue, component group).

* [**_Aug 31_**](./sourceFiles/Aug31): The quality and feasibility of symptom clustering were evaluated using new methods and studying the clusters inside each product group. Different methods were tried for increasing the quality of clustering. 

***
***

<a name="end">
### **Final Versions of Codes and Their Running Tips**
</a>

The following sections describe the final versions of the codes for accomplished works that are required for running my pipeline. The codes are tried to be as simple as possible and be easily run in shell with few arguments. Each of the following sections demosntrates the codes running in shell and the resulting outputs.   

***
#### [**_Raw log data extraction codes_**](./sourceFiles/finalVersions/hive)
<a name="hive">
</a>

The codes applied here are written in bash and Hive for pulling the data out of symptoms, classification, feedback tables in aml_cg database, between the given start and end dates as arguments. The pulled data will be from begining of the start date (00:00:00) to the end of the end date (23:59:59). The schema used for pulling data out hive here will be applied by the following codes for data extraction. Code should be run in "searchp".

_Inputs_:
- Start date (format: YYYY-mm-dd)
- End date (format: YYYY-mm-dd)

_Outputs_:
- symptoms_$startDate_$endDate.txt
- classifications_$startDate_$endDate.txt
- feedback_$startDate_$endDate.txt


Demonstration:
```bash
bash-4.1$ bash hiveRunner_Eliyar.sh 2016-06-01 2016-06-03

Getting data from 2016-06-01 to  2016-06-03  (from symptom, classification, feedback tables in the aml_cg database)
16/09/02 18:50:03 INFO Configuration.deprecation: mapred.input.dir.recursive is deprecated. Instead, use mapreduce.input.fileinputformat.input.dir.recursive
.
.
.
OK
Time taken: 2.355 seconds
Total MapReduce jobs = 1
Launching Job 1 out of 1
.
.
.
2016-09-02 18:50:51,879 Stage-1 map = 0%,  reduce = 0%
.
.
.
2016-09-02 18:54:45,674 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 1079.73 sec
MapReduce Total cumulative CPU time: 17 minutes 59 seconds 730 msec
Ended Job = job_1446237185892_226585
Moving data to: tempCGData_1726354527182735_2016-06-01_2016-06-03/symptoms
MapReduce Jobs Launched: 
Job 0: Map: 299   Cumulative CPU: 1079.73 sec   HDFS Read: 17996923639 HDFS Write: 60923531 SUCCESS
Total MapReduce CPU Time Spent: 17 minutes 59 seconds 730 msec
OK
source	requesttype	_c2	testid	requestid	traceid	start_timestamp	end_timestamp	start_datetime	end_datetime	timestamp_inrequestdata	_c11	productgroupfamilyid	productgroupid	affectedproductid	eligibleproductid	agentid	symptom_suggestions	month	year
Time taken: 282.389 seconds
.
.
.
2016-09-02 18:56:23,026 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 622.08 sec
MapReduce Total cumulative CPU time: 10 minutes 22 seconds 80 msec
Ended Job = job_1446237185892_226589
.
.
.
2016-09-02 18:58:11,014 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 2156.98 sec
MapReduce Total cumulative CPU time: 35 minutes 56 seconds 980 msec
Ended Job = job_1446237185892_226593
Moving data to: tempCGData_1726354527182735_2016-06-01_2016-06-03/feedback
MapReduce Jobs Launched: 
Job 0: Map: 481   Cumulative CPU: 2156.98 sec   HDFS Read: 33704147907 HDFS Write: 29969837 SUCCESS
Total MapReduce CPU Time Spent: 35 minutes 56 seconds 980 msec
OK
source	requesttype	request_data	testid	start_timestamp	end_timestamp	start_datetime	end_datetime	timestamp_inrequestdata	query	productgroupfamilyid	productgroupid	affectedproductid	eligibleproductid	agentid	caseid	classificationset	selected_classification
Time taken: 108.936 seconds

16/09/02 19:00:35 INFO fs.TrashPolicyDefault: Namenode trash configuration: Deletion interval = 86400000 minutes, Emptier interval = 0 minutes.
Moved: 'hdfs://ma1-rspp-lnn.corp.apple.com/user/searchp/tempCGData_1726354527182735_2016-06-01_2016-06-03' to trash at: hdfs://ma1-rspp-lnn.corp.apple.com/user/searchp/.Trash/Current

-bash-4.1$ ls -al
total 4986052
.
.
.
-rw-r----- 1 searchp searchp   30079806 Sep  2 19:00 classifications_2016-06-01_2016-06-03.txt
-rw-r----- 1 searchp searchp   33671451 Sep  2 19:00 feedback_2016-06-01_2016-06-03.txt
-rw-r----- 1 searchp searchp   68607340 Sep  2 19:00 symptoms_2016-06-01_2016-06-03.txt


```

***
#### [**_Log data extraction/processing code_**](./sourceFiles/finalVersions/logDataExtractionCodes)

The code is written in python for extracting comprehensive information by processing the pulled raw log data (using [codes](./sourceFiles/finalVersions/hive) explained above).  

_Required libraries_:
- pandas
- numpy 
- re
- os
- sys
- time
- warnings
 
_Inputs_:
- Address of curation dictionary (in .xlsx format)
- Address of pulled symptom files from hive ([above](#hive))
- Address of pulled classification files from hive ([above](#hive))
- Address of pulled feedback files from hive ([above](#hive))
- Address of directory that contains Product, Component, Issue mapping files with the following names (if the names change minor corrections are required):
    - productToGroupMap_v4.0.xlsx
    - componentMap_v4.0.xlsx
    - issueMap_v4.0.xlsx
- Time interval that data represents (optional, used for tagging)
- Separator used in files for separating columns in each row (optional, default is "::-::-::")

_Outputs_:
- Combined symptom(S), classification(C), feedback(F) tables (grouped by Test ID)
- Log data extracted based on "last S - last C - last F" pattern (marked by SCF)
- Log data extracted based on consecutive "SC" and "CF" patterns (marked by SC-CF)
- Reformatted SCF file for new symptom detection (NSD) pipeline.
- Reformatted SC-CF file for new symptom detection (NSD) pipeline.
- Eligible products with codes not existing in the mapping files (if any)
- Components with codes not existing in the mapping files (if any)
- Issues products with codes not existing in the mapping files (if any)

_Sample files_:
[symptoms_05_16-05_22-2016.txt, classifications_05_16-05_22-2016.txt, feedback_05_16-05_22-2016.txt](./sourceFiles/finalVersions/logDataExtractionCodes)

[symptomClassification.xlsx, dictionary_mappingFiles](./sourceFiles/symptomClassificationFiles)


Demonstration:
```bash
python logDataExtractionCodes_final.py [./symptomClassification.xlsx](./sourceFiles/symptomClassificationFiles) ./symptoms_05_16-05_22-2016.txt ./classifications_05_16-05_22-2016.txt ./feedback_05_16-05_22-2016.txt [./dictionary_mappingFiles/](./sourceFiles/symptomClassificationFiles) 05_16-05_22 

 ----------------------------------------------------------------------------------------------------
Loading S, C, and F log data and preparing/combining them ...
Progress: S, C, and F data prepared and combined. Time spent: 3.74 minutes.


 ----------------------------------------------------------------------------------------------------
Loading/preparing the symptom-classification dictionary ... 
Dictionary loaded and prepared.

 ----------------------------------------------------------------------------------------------------
Starting post-processing the combined log data (SCF patterns)... 
Progress: 100%

Log data post-processing (SCF pattern) completed. Time spent: 10.33 minutes.



 ----------------------------------------------------------------------------------------------------
Starting post-processing the combined log data (SC and CF patterns)... 
Finding SC and CF patterns for each testID.
Progress: 100%
Processing the data for each testID and its SC and/or CF patterns.
Progress: 100%

Log data post-processing (SC and CF patterns) completed. Time spent: 19.97 minutes.


 ----------------------------------------------------------------------------------------------------
Saving the final results in a proper format for feeding into the New Symptom Detection pipeline.

 ----------------------------------------------------------------------------------------------------
Process finished. Total time spent: 34.51 minutes.


```


***
#### [**_Dictionary expansion code (SCIs in product groups)_**](./sourceFiles/finalVersions/dictionaryExpansionByPropagation)

The code is written in python for expanding the dictuonary by propagating the symptoms/classifications (PCI) among products belonging to the same product groups. The groups are defined subjectively (confirmed by the AML CG team) and can be changed inside the code. 

_Required libraries_:
- pandas
- os
- sys

_Inputs_:
- Address of curation dictionary (in .xlsx format)
- Address of directory that contains Product, Component, Issue mapping files with the following names (if the names change minor corrections are required):
    - productToGroupMap_v4.0.xlsx
    - componentMap_v4.0.xlsx
    - issueMap_v4.0.xlsx

_Outputs_:
- The expanded dictionary
- The expanded components mapping file
- The expanded case issue mapping file

_Sample files_:
[symptomClassification.xlsx, dictionary_mappingFiles](./sourceFiles/symptomClassificationFiles)


Demonstration:
```bash
python dictionaryExpansionByPropagation_final.py ./symptomClassification.xlsx ./dictionary_mappingFiles

 ----------------------------------------------------------------------------------------------------
Reading preparing dictionary ...

 ----------------------------------------------------------------------------------------------------
Reading the mapping files and preparing translation dictionary ...

 ----------------------------------------------------------------------------------------------------
Expanding the dictionary based on the defined product groups ...
(181807, 11)
Finished expanding the dictionary. Time spent: 2.3 minutes.


```


***
#### [**_Dictionary expansion evaluation code_**](./sourceFiles/finalVersions/dictionaryExpansionEvaluationCodes)

The code is written in python for evaluating the effect of expanding the curation dictuonary by propagating the symptoms/classifications (PCI) among products belonging to the same product groups as well as using SETI symptoms.

_Required libraries_:
- pandas
- numpy
- collections
- sys
- os
- time 

_Inputs_:
- Address of the expanded curation dictionary in .xlsx format
- Address of extracted log data (using the log data extraction/processing pipeline) in .csv format. The files with SCF
or SC-CF tags in the outputs from running this pipeline can be used.
- Address of the file containing confirmed/added SETI symptoms in .xlsx format. This file should have one sheet with
 the SETI symptoms in its first column.
- Time interval that data represents (optional, used for tagging)

_Outputs_:
- Coverage and CTR metrics
- Measured effects of adding SETI symptoms to the dictionary
- Measured effects of propagation symptom-classifications for defined product groups
- Meta data that summarizes the total effects

_Sample files_:
[symptomClassification_v4.2_expanded.xlsx, ./logExtracted_SCF_TestIDgrps_05_16-05_22.csv, ./acceptedSETIsymptoms.xlsx 05_16-05_22](./sourceFiles/finalVersions/dictionaryExpansionEvaluationCodes)


Demonstration:
```bash
python dictionaryExpansionEvaluationCodes_final.py ./symptomClassification_v4.2_expanded.xlsx ./logExtracted_SCF_TestIDgrps_05_16-05_22.csv ./acceptedSETIsymptoms.xlsx 05_16-05_22

 ----------------------------------------------------------------------------------------------------
Loading/preparing the symptom-classification dictionary ... 
Dictionary loaded and prepared.

 ----------------------------------------------------------------------------------------------------
Loading and preparing the extracted log file ...
The extracted log file loaded and prepared.

 ----------------------------------------------------------------------------------------------------
Starting metric calculations ... 

Measuring the effect of expanding the symptom-classification dictionary by the SETI symptoms ...
Progress: 100%

Measuring the effect of expanding the symptom-classification dictionary by the propagation ...
Progress: 100%
Done with the metric calculation.
numSymp =  29279
numClass =  42863
numSympSugg =  11453
numClassSugg =  5412
numSympClicked =  4402
numClassClicked =  2633
Numbers of Classification suggestion with at least one Propagated case =  529
Numbers of Final Classification Coming from Propagations 521
Numbers of Final Classification Coming from Propagations (clicked) 212
Number of Symptoms Suggestions with at Least one fromSETI 25
Numbers of Final Symptom Coming from SETI 2
Numbers of Final Symptom Coming from SETI (clicked) 2

 ----------------------------------------------------------------------------------------------------
Process finished. Total time spent: 3.93 minutes.


```


***
#### [**_Symptoms keywords expansion and weighting code_**](./sourceFiles/finalVersions/symptomExpansionWeighting)

The code is written in python for expanding (dictionary) symptoms using a trained Word2Vec model and for weighting the symptoms based on their CTR in the log data.

_Required libraries_:
- pandas
- numpy
- Support
- gensim
- sys
- os
- time 
- warnings

_Inputs_:
- The address of a .csv file that contains at least one column of string data (Symptoms).
- The address of a .csv file that is extracted from the log data, and contains at least two columns of string data
  named as "SymptomSuggestions" and "symptomClickPosition". The symptom suggestions should be strings separated with a
  separator that is either assumed as a default value considered below or the one determined as input.
- The address of the trained word2vec model used for expanding the symptoms by adding keywords.
- A symbol used as separator for separating the symptom suggestions (the default is "::-::-::").

_Outputs_:
- A .csv file with three columns: 1) Symptoms, 2) added keywords, 3-4) calculated weights for the given symptom
(CTR and CTR - 1 * sd).

_Sample files_:
[word2vecModelTrainedOnSupportData.bin](./sourceFiles/trainedModels)


Demonstration:
```bash
python ./symptomExpansionWeighting_final.py ./sampleSymps.csv ./sampleLogExtr.csv word2vecModelTrainedOnSupportData.bin

 ----------------------------------------------------------------------------------------------------
Loading/preparing the input symptom files for expansion and weighting based on the log data ... 
The data is loaded and prepared.

 ----------------------------------------------------------------------------------------------------
Starting the symptoms expansion by keywords generation, have a cup of coffee or maybe take a nap :) ... 

Training TFIDF model for selecting top words for expansion by keyword generation ... 
TFIDF model is trained.

Selecting top words in each canonical symptom based on the TFIDF model ...
Top words are selected for expansion.

Loading the trained Word2Vec model for keywrod generation ... 
The Word2vec model is loaded.

Starting the keyword generation for the selected words for each symptom (this can take a while)...
Progress: 100%

The keywords generation finished. Time spent: 0.43 minutes.

 ----------------------------------------------------------------------------------------------------
Finding CTRs for the symptoms using the loaded log data ...
Progress:   0%Progress: 100%
100%

CTRs calculated. Time spent: 0.01 minutes.

 ----------------------------------------------------------------------------------------------------
Process finished. Total time spent: 0.99 minutes.


```


***
#### [**_Symptoms clustering code_**](./sourceFiles/finalVersions/dictionarySymptomClustering)

The code is written in python for running hierarchical clustering using the provided Symptoms-Keywords file and Doc2Vec model for vectorization. The distance to separate clusters is found by tuning the clustering models before hand using the provided labeled data. This distance can be changed inside the code using the "MAX_DIST" variable.

_Required libraries_:
- pandas
- numpy
- Support
- gensim
- sys
- os
- scipy
- sklearn
- pickle
- time 

_Inputs_:
- The address to a .csv file with at least two columns:
    - Symptoms
    - Keywords (comma separated)
- The address to the trained Doc2Vec model used for vectorization.

_Outputs_:
- A .csv file similar to the input with additional columns that identifies the clusters and their size.

_Sample files_:
[trainedModelBySupportBodyData_highDimVectords100](./sourceFiles/trainedModels)


Demonstration:
```bash
python dictionarySymptomClustering_final.py ./sampleForClustering.csv ./trainedModelBySupportBodyData_highDimVectords100

 ----------------------------------------------------------------------------------------------------
Loading/preparing the dictionary symptoms by expanding them using the provided keywords ... 
dictionary symptoms expanded/prepared.

 ----------------------------------------------------------------------------------------------------
Loading previously trained NLP model by the Support package ... 
Model loaded.

 ----------------------------------------------------------------------------------------------------
Finding the feature vectors for the expanded symptoms using the trained Doc2Vec model ... 
Feature vectors calculated and saved.

 ----------------------------------------------------------------------------------------------------
Starting clustering the symptoms using the feature vectors of the expanded symptoms ... 
Clusters found based on the defined maximum distance (= 0.3).

 ----------------------------------------------------------------------------------------------------
clustering process finished and the results are saved. Total time spent: 16.91 minutes.


```


***
#### [**_n-grams model (type ahead table) code_**](./sourceFiles/finalVersions/nGramModel)

The code is written in python for running hierarchical clustering using the provided Symptoms-Keywords file and Doc2Vec model for vectorization. The distance to separate clusters is found by tuning the clustering models before hand using the provided labeled data. This distance can be changed inside the code using the "MAX_DIST" variable.

_Required libraries_:
- pandas
- numpy
- nltk
- re
- os
- sys
-time

_Inputs_:
- A .csv file containing a symptom column (called "symptom" by default)
- Extracted file from log (using symptoms and classification tables) with at least two columns:
    - Typed query: typed symptom in symptom table (named 'typedQuery' by default)
    - Symptom: the symptom in the dictionary that represent typed symptom (clicked symptom in classification table,
    called "symptom" by default).
- Extracted log file with at least two columns called "symptomSuggestions" and "symptomClickPosition" for scoring the
symptoms based on win, loss, tie situations.

_Outputs_:
- A .csv file with n-grams (n = 1-5) with the following schema: 'typeahead', 'symptom', 'method_type', "Win", "Loss",
"Tie", "AverageWinPosition", 'weight'
    - 'typeahead': infix n-gram
    - 'symptom': the symptom used for finding infix n-gram
    - 'method_type': a tag for the applied n-gram
    - 'Win': numbers of wins based on log
    - 'Loss': Numbers of loss based on log
    - 'Tie': Numbers of ties based on log
    - 'weight': weights defined using the defined link function (see the function inside code)

_Sample files_:
[symptomDictionary.csv, typedQuerySample.csv, logDataSample.csv](./sourceFiles/finalVersions/nGramModel)


Demonstration:
```bash
python nGramModel.py symptomDictionary.csv typedQuerySample.csv logDataSample.csv 

 ----------------------------------------------------------------------------------------------------
Finding ngrams for (dictionary) symptoms and typed queries in clicked data (in the log) ... 

 ----------------------------------------------------------------------------------------------------
Calculating scores for symptoms based on win, loss, tie situations... 
Progress:   0%Progress: 100%
100%


```


***
#### [**_n-grams model evaluation code_**](./sourceFiles/finalVersions/nGramModel)

The code is written in python for running hierarchical clustering using the provided Symptoms-Keywords file and Doc2Vec model for vectorization. The distance to separate clusters is found by tuning the clustering models before hand using the provided labeled data. This distance can be changed inside the code using the "MAX_DIST" variable.

_Required libraries_:
- pandas
- sys
-re

_Inputs_:
- The output of nGramModel.py

_Outputs_:
- The log data (from log data extraction pipeline) for assessing coverage of the n-gram model.

_Sample files_:
[logNgrams_tokensLetters_winLossTieWeighted.csv, logExtracted_SC_CF_TestIDgrps_07_25-07_31.csv](./sourceFiles/finalVersions/nGramModel)


Demonstration:
``` bash
python ngramModelAssessment.py ./logNgrams_tokensLetters_winLossTieWeighted.csv ./logExtracted_SC_CF_TestIDgrps_07_25-07_31.csv 

 ----------------------------------------------------------------------------------------------------
The coverage of n-grams (type ahead) model for in the given log (all log) is: %s 0.18243859589851008

 ----------------------------------------------------------------------------------------------------
The coverage of n-grams (type ahead) model for in the given log (with no suggestion) is: %s 0.18243859589851008

 ----------------------------------------------------------------------------------------------------
The coverage of n-grams (type ahead) model for in the given log (using clicked data) is: %s 0.7452830188679245


```


***
#### [**_Dictionary expansion by propagating (products for Apps component and iCloud/iTunes/Apple ID) code_**](./sourceFiles/finalVersions/dictionaryExpansionByPropagation)

The code is written in python for running hierarchical clustering using the provided Symptoms-Keywords file and Doc2Vec model for vectorization. The distance to separate clusters is found by tuning the clustering models before hand using the provided labeled data. This distance can be changed inside the code using the "MAX_DIST" variable.

_Required libraries_:
- pandas
- sys
- re
- time

_Inputs_:
- symptom-classification file in .xlsx format
- Product group mapping file in .xlsx format

_Outputs_:
- The expanded dictionary by propagation in .csv and .xlsx formats

_Sample files_:
[symptomClassification.xlsx, productToGroupMap.xlsx](./sourceFiles/symptomClassificationFiles)


Demonstration:
```bash
python productPropagation_AppsIOS_iCloudItumesAppleID_final.py ./symptomClassification.xlsx ./productToGroupMap.xlsx

 ----------------------------------------------------------------------------------------------------
Propagating products for Apps component between ios devices ...

 ----------------------------------------------------------------------------------------------------
Propagating products iCloud, iTunes, Apple ID ...

 ----------------------------------------------------------------------------------------------------
Dictionary expansion by propagation finished. Total time spent: 3.92 minutes.


```


***
#### [**_New symptom detection code_**](./sourceFiles/finalVersions/newSymptomDetection)

The code is written in python for finding new symptom candidates. The applied process/algorithm is as the following:

- Finding cleaned symptoms in the log using the filtering (cleaning) pipeline in Support package.
- Finding the frequency of the cleaned symptoms.
- Filtering out rows of extracted log data based on the defined frequency threshold
- Measuring the varioations in frequency of symptoms over time (not applied in the pipeline yet) for three groups:
    - All data
    - Inside component-issue groups
    - Inside affected product-component-issue groups
    
- Measuring the similarities between log data symptoms and the ones in the dictionary as well as the agents contributed to typing the symptoms for:
    - All data
    - Inside component-issue groups
    - Inside affected product-component-issue groups
- Narrowing down on new symptom candidates based on defined thresholds for similarities as well as agents contributions
- Performing clustering and selecting the presentations for the new symptom candidates
- Preparing output for Kevin-Saurav's pipeline


_Required libraries_:
- pandas
- numpy
- sys
- os
- re
- scipy
- collections
- Support (Support_final)
- collections
- warnings

_Inputs_:
- Address of the curation dictionary in .xlsx format
- Address of extracted log data (using the log data extraction/processing pipeline) in .csv format. The files with SCF
or SC-CF tags in the outputs from running this pipeline can be used.
- Address of the trained Dco2Vec model for vectorization and clustering.
- Date period used for new symptom detection (optional)
- Separator used in extracted log file for separating suggestions in suggestion list (optional if default separator is used)

_Outputs_:
- Selected slice of log data for use in the rest of pipeline (simple filtering rows)
- Post processed log data with added information for measuring changes in frequency over time
- Post processed log data with added information on similarities of symptoms to the existing symptoms in the dictionary.
- Selected candidates at the first round based on the defined thresholds
- Selected candidates cleaned based on similarities (using clustering)
- Selected new symptoms in a proper format for Kevin-Saurav's pipeline (for getting canonical forms)

_Sample files_:
[symptomClassification.xlsx, logExtracted_SCF_TestIDgrps_ForNSDpipeline_05_16-05_22.csv](./sourceFiles/finalVersions/newSymptomDetection)
[trainedModelBySupportData_May27](./sourceFiles/models)

Demonstration:
```bash
python newSymptomDetection_final.py ./symptomClassification.xlsx ./logExtracted_SCF_TestIDgrps_ForNSDpipeline_05_16-05_22.csv trainedModelBySupportData_May27

 ----------------------------------------------------------------------------------------------------
Loading/preparing the symptom-classification dictionary ... 
Dictionary loaded and prepared.

 ----------------------------------------------------------------------------------------------------
Loading the extracted/prepared file from the log data (by previous pipeline), and preparing it for New Symptom Detection pipeline ...
The extracted data from the log is loaded and ready for starting the New Symptom Detection pipeline.

 ----------------------------------------------------------------------------------------------------
Loading previously trained NLP model by the Support package ... 
Model loaded.

 ----------------------------------------------------------------------------------------------------
Measuring the time variations for the frequency of symptoms in the log by increasing level of granularity (and merging the results):
1. Cleaned symptoms 
2. Cleaned symptoms in the log per CI group 
3. Cleaned symptoms in the log per PCI group 

1. Cleaned symptoms/Day groups (numbers of groups to aggregate: 411)
Progress: 100%

2. Component-Issue/Day groups (numbers of groups to aggregate: 632)
Progress: 100%

3. ...

3. Product-Component-Issue/Day groups (numbers of groups to aggregate: 1278)
Progress: 100%

Measuring the time variations of frequencies finished. Time spent: 0.07 minutes.

 ----------------------------------------------------------------------------------------------------
Finding the most similar symptoms in the dictionary for each symptom in the log by increasing level of
granularity (and merging the results): 
1. Cleaned symptoms in the log against all symptoms in the dictionary. 
2. Cleaned symptoms in the log per CI group against symptoms in the dictionary for the CI group (if found any).
3. Cleaned symptoms in the log per PCI group against symptoms in the dictionary for the PCI group (if found any).

1. Cleaned symptoms groups (numbers of groups to aggregate: 59)
Progress: 100%

2. Component-Issue groups (numbers of groups to aggregate: 209)
Progress: 100%

3. Product-Component-Issue groups (numbers of groups to aggregate: 533)
Progress: 100%

Similar symptoms per defined groups found. Time spent: 4.37 minutes.

 ----------------------------------------------------------------------------------------------------
Selecting new symptom candidates based on the defined thresholds and preparing the results.
Progress: 100%
./Report Documents and Codes/allWorks/sourceFiles/finalVersions/newSymptomDetection/newSymptomDetection_final.py:731: SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
  logSims_selectForFinalStep['ORIGINAL SYMPTOM']]

 ----------------------------------------------------------------------------------------------------
Process finished. Total time spent: 9.39 minutes.


```





***
***


