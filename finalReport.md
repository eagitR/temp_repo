# Final Report

#### Eliyar Asgarieh 
##### September 1, 2016

***
***

## Summary

The following report is prepared for presenting my contribution to the CG project in organized form as well as facilitating the next contributions to the project. The works are first represented in chronological order for better understanding the evolution of the works in the project. The latest versions of the codes are represented at the end of the report. So, the hasty reader may want to just skip to the final section. In the following, the date headers in bullet points indicate when the works or final results are presented. 

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
### **Final Versions of Codes and Their Running Tips**

The following sections describe the final versions of the codes for accomplished works that are required for running my pipeline. The codes are tried to be as simple as possible and be easily run in shell with few arguments. Each of the following sections demosntrates the codes running in shell and the resulting outputs.   

##### Codes for Getting Log Data From Hive

These codes pulls the data out of symptoms, classification, feedback tables in aml_cg database, for the given start and end dates as arguments. The pulled data will be from begining of the start date (00:00:00) to the end of the end date (23:59:59). The schema used for pulling data out hive here will be applied by the following codes for data extraction. Codes should be run in "searchp".

Inputs:
- Start date (format: YYYY-mm-dd)
- End date (format: YYYY-mm-dd)

Outputs:
- symptoms_$startDate_$endDate.txt
- classifications_$startDate_$endDate.txt
- feedback_$startDate_$endDate.txt

Code running demonstration:
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

##### Log Data Extraction Code

*Inputs*:
- 


