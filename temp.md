
#Final Report

***

#### Eliyar Asgarieh 
#####September 9, 2016
=======================================


##Summary

The following report is prepared for presenting my contribution to the CG project in organized form as well as facilitating the next contributions to the project. The works are first represented in chronological order for better understanding the evolution of the works in the project. The works that are completed or supposed to be completed in future are represented. The hasty reader may want to just skip to the final section.

### **Initial Studies on the Dictionary and the Log Data**

The research began by studying the existing symptoms and classifications - Affected Product, Component, and Case Issue (PCI) - in the dictionary and their distributions under each clicked/typed symptom/classification categories. The following bullet points summarizes the works and results during this stage. The date headers in bullet points indicate when the works or final results are presented. 

* **_March 7_**: the performance of the current suggestion system was initially investigated (using the statistics prepared by the HyunJooon), and the outline of the project based on the initial brain storming on the project’s road plan were in the CG meeting. The gist of the initial ideas was:
    - Clustering symptoms in separate defined clusters.
    - Ranking PCIs under each cluster based on the extractable information from the dictionary such as their frequency.
    - Comparing the incoming query with symptoms clusters and finding the cluster with highest aggregate similarity.
    - Suggesting the highest ranked classifications.

* **_March 22_**: the dictionary was studied in more detail to better understand the diversity of classifications (especially CIs) inside groups defined by symptoms and (eligible) product groups. 
    - Results: It was shown that while there can be many cases for which there are less than 3 classifications, but the numbers of cases with high numbers of classifications are still very considerable. (It should be mentioned that this study was made before dictionary expansion, and by expanding the dictionary as well as adding new data to the dictionary, the results can be much more diverse and numbers of classifications under each category after symptom selection will be higher).
        
* **_March 29_**: the work on the log data was started. Initial statistics coverage and CTR were calculated. Also, the pattern in symptom/classification suggestions and clicks were initially studied. The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered.
	
* **_April 12_**: the work on the log data was continued. The distribution of symptom suggestions and typing-clicking patterns per P.C. as well as agent groups were studied. It was shown that some P.C. groups attract more symptom suggestions. Another part of this study was on the agent’s behavior. It was illustrated that some agents are more into typing habits than the others. The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered.

* **_April 21_**: The distribution of symptoms-classifications pairs based on the defined clicked-or-typed categories were studied using the updated log data. It was shown that the majority of the data fell into the typed symptom-typed classification category. Also, it was shown that there are cases in which final correct classification was suggested but it was not clicked by the agents. The numbers in this study may not be very accurate since the data extracted from the log is just based on rows, and the role of Test IDs were not considered.

***
### Starting Work on the CG Project Pipeline
The following works on the project has more organized and purposeful form after the initial exploratory and try and error phase. The following lines summarize the performed research and achievements during this stage. 

* **_May 3_**: The following bullets summarizes the collection of tasks performed between April 21 and May3. 
o	The research was reorganized and a presentation were prepared to summarize the problem, involved challenges, applicable methodologies, and the base pipeline considered for the project at that time. 
o	The relationship between eligible and affected products as well as product groups were briefly studied by bi-partite graphs. It was shown that some product (groups) such as iCloud and iTunes are attracting considerably more eligible products. 
o	New codes were written for the log data extraction using the Test ID column in the log data to extract more comprehensive and accurate information from the log.
o	The Doc2Vec model from the “genism” library in Python were trained using the extracted data from the log as well as the dictionary for vectorization.
o	Python Packages were written for CG and Support projects. These packages (especially Support package) are extensively used during the project for data extraction/cleaning and model training as well as prediction purposes. 
o	An initial classification machine learning model based on the information from the log and dictionary were designed and implemented in the CG package. This model is not tested and used yet (August 16). 
•	May 9: Connecting of rows of the log was confusing and calculating unique metrics from data proved to be tricky. The extracted data from the log by HyunJoon was used for calculating metrics and studying the log during this week (May 3-9). The codes written during this week can be used on the log data extracted by the HyunJoon. Later on, newer versions of codes were written for comprehensive data extraction using raw log data. 
•	May 24: Comprehensive and accurate codes were written in Python for extracting extensive ranges of information and metrics from the raw log data. These codes (with limited updates) are used through the project for weekly analysis of log data. The codes extract data based on both last S, last C, last I pattern and separate SC-CF patterns for each test ID. The comprehensive information extracted using these codes can be found in the report prepared for the meeting held on this date. It was clear from the metrics that the coverage for symptom/classification suggestions are very low.    
•	May 31: To increase the coverages, it was decided to expand the symptom-classification dictionary by propagating the Symptoms-Components-Issues for the similar products. The codes were written in Python for dictionary expansion using set of defined product groups.  The results of this expansion were sent to update the applied dictionary in the system. 
o	The other jobs accomplished during this week (continued from weeks before) was training the Doc2Vec models using extracted data from the support data. The data extraction and model training were done using the modules in the Support package. 
•	June 10: The following bullets summarize the tasks performed during first week of June.
o	Dictionary symptom clustering: Since many symptoms in the dictionary are suspected to be semantically or syntactically similar, clustering was done on the dictionary symptoms (using the vector presentations of symptoms by the trained Doc2Vec models). The results were sent for expert review. The research on the symptom clustering has been continued in later weeks by trying various vectorization and clustering approaches. 
o	Other important tasks that started this week and continued through later weeks is writing the new symptom detection (NSD) pipeline. This pipeline has been changed/revised during following weeks (after June 10) for increasing its accuracy and efficiency. 
•	June 22: The following are the tasks performed by this date:
o	The effect of dictionary expansion by propagation and adding SETI symptoms was evaluated. The results were reported to be used by the group for preparing presentation slides (for meeting with managers from other departments). Evaluation the effect of dictionary expansion was very challenging since there was a huge inconsistency between PCI cases (Capital letter, lower case, upper case, etc.) in the log, dictionary, and mapping files. These codes are updated in later weeks for resolving problems related to cases sensitivity. 
•	June 17: The log data extraction codes and dictionary expansion evaluation codes were updated for better quality and performance. The results were communicated with the group, through meeting. 
•	July 29: The idea of keyword expansion for the symptoms were tried. The top tokens in symptoms were selected based on their TFIDF scores, and were expanded using different Word2Vec models by adding similar words to them. In addition, the symptoms were weighted using their CTRs extracted from the log data. This approach were tried and evaluated in the following weeks. 
•	Aug 1: The following are the works finished for this date:
o	More work was done on dictionary symptom clustering and codes were refined. The expanded symptoms by the Word2Vec model keywords were used for vectorization and clustering. The results are not very promising, since adding keywords can add noise to the data and make similar symptoms very dissimilar. 
o	The NSD pipeline were revised to be adapted with the Kevin-Saurav’s pipeline for normalizing symptoms.
•	Aug 9: Clustering algorithms were tuned using limited available labeled data on the previously prepared clusters. The optimum parameters were obtained to be used for later clustering steps. 
•	Aug 12: The idea of increasing symptom coverage by adding n-grams as type-aheads to the data was tried. All combinations of token and letter n-grams were found for symptoms and a data table were prepared for the symptoms in the dictionary. The symptoms were weighted based on their CTR in the log data.
•	Aug 17: The effect of n-grams model for symptom coverage were assessed. The results were not very promising since the n-gram model is very restricted on the order of the words. 
•	Aug 24: The codes for dictionary expansion by propagation for “Apps” component in iOS devices as well as for “iCloud”, “iTunes”, and “Apple ID” group were written. The symptoms and issues were propagated for groups, and the results were shared through email.
•	Aug 29: The codes for dictionary expansion by propagation were corrected based on the request. The codes were changed to propagate Eligible products (= Affected Products) for all iOS devices that have Apps component (for each symptom and issue); And, the Eligible products for all the “iCloud”, “iTunes”, and “Apple ID” groups (for each symptom, issue, component group).

