
"""
Created on June 10, 2016

@author: eliyarasgarieh
________________________________________________________________________________

This file is written to be used as an initial pipeline for new symptom detection.
It uses the following packages:
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

Inputs:
- Address of the curation dictionary in .xlsx format
- Address of extracted log data (using the log data extraction/processing pipeline) in .csv format. The files with SCF
or SC-CF tags in the outputs from running this pipeline can be used.
- Address of the trained Dco2Vec model for vectorization and clustering.
- Date period used for new symptom detection (optional)
- Separator used in extracted log file for separating suggestions in suggestion list (optional if default is used)

Outputs:
- Selected slice of log data for use in the rest of pipeline (simple filtering rows)
- Post processed log data with added information for measuring changes in frequency over time
- Post processed log data with added information on similarities of symptoms to the existing symptoms in the dictionary.
- Selected candidates at the first round based on the defined thresholds
- Selected candidates cleaned based on similarities (using clustering)
- Selected new symptoms in a proper format for Kevin-Saurav's pipeline (for getting canonical forms)

"""

import pandas as pd
import numpy as np
import re
import sys, os
from collections import defaultdict
from Support_final.filters import filter_
import Support_final
from time import time
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import fcluster
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Recording the total run time (printed at the end)
ALL_START = time()

# Reading command line arguments and assigning the values to (constant) variables.
args = sys.argv

DICT_ADDRESS = args[1]
LOG_EXTRACTED_ADDRESS = args[2]
TRAINED_MODEL_ADDRESS = args[3]
DATE_PERIOD = ''
SEP = "::-::-::"  # especial separator used since the tab and comma where hard to use due to condition of the text data
if len(args) > 4: DATE_PERIOD = args[4]
if len(args) > 5: SEP = args[5]

TIME_COLUMN = 'start_datetime'
SYMPTOM_COLUMN = 'Symptoms'
PRODUCT_COLUMN = 'AffectedProduct'
COMPONENT_COLUMN = 'Component'
ISSUE_COLUMN = 'CaseIssue'
AGENT_COLUMN = 'agentID'
CLEANED_SYMPTOM = 'cleanedSymptoms'  # To be added after loading the extracted log data.

SOURCE = '.'
DEST_LOG_EXTRACTED_POSTPROCESSED = os.path.join(SOURCE, "logExtracted_PostProcessed_%s.csv" % DATE_PERIOD)
DEST_ADDRESS_LOG_FREQ_BY_TIME = os.path.join(SOURCE, "logSymptomsFrequencyTimeVariation_%s.csv" % DATE_PERIOD)
DEST_ADDRESS_LOG_DICT_SIMS = os.path.join(SOURCE, "logDictSimilarity_%s.csv" % DATE_PERIOD)
DEST_ADDRESS_NEWSYMP_SELECTED_CANDIDATES = os.path.join(SOURCE, "newSymptomsSelectedCandidates_%s.csv" % DATE_PERIOD)
DEST_ADDRESS_NEWSYMP_SELECTED_CANDIDATES_ = os.path.join(SOURCE,
                                                         "newSymptomsSelectedCandidates_removedSimliars_%s.csv" \
                                                     % DATE_PERIOD)
DEST_ADDRESS_NEWSYMP_FOR_FINAL_STEP = os.path.join(SOURCE, "newSymptomsForFinalStep_%s.csv" % DATE_PERIOD)
DEST_ADDRESS_SYMPTOMS_FOR_REFORMATTING = os.path.join(SOURCE , "newSymtomsForKevinSuaravsPipeline_%s.csv" % DATE_PERIOD)

# Thresholds for selecting new symptom candidates
FREQUENY_THRESHOLD = 30
PCIGRP_SIMILARITY_THRESHOLD = 1.0001
CIGRP_SIMILARITY_THRESHOLD = 0.6
ALL_SIMILARITY_THRESHOLD = 0.7
NUM_AGENTS_THRESHOLD = 3

# A wrapper function for showing progress of the "apply" function on the groups.
def progress(g, func, *args, **kwargs):

    sys.stdout.write('Progress:   0%')
    sys.stdout.flush()
    deltaComplete = 100. / len(g)

    def logger(func):
        def counter(*args, **kwargs):
            progress_ = counter.count * deltaComplete
            sys.stdout.write('\033[D \033[D' * 4 + format(progress_, '3.0f') + '%')
            sys.stdout.flush()
            counter.count += 1
            return func(*args, **kwargs)
        counter.count = 0
        return counter

    funcInProgress = logger(func)
    res = g.apply(funcInProgress, *args, **kwargs)
    sys.stdout.write('\033[D \033[D' * 4 + format(100., '3.0f') + '%' + '\n')
    sys.stdout.flush()
    return res

#______________________________________________________________________________________________________________________#
# Loading and preparing the dictionary
print('\n', '-'*100)
print("Loading/preparing the symptom-classification dictionary ... ")

dict_ = pd.read_excel(DICT_ADDRESS)
dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']] = \
    dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']].replace(np.nan, '')
dict_.loc[['NON'.lower() in x.lower() and 'TECHNICAL'.lower() in x.lower() and 'ISSUE'.lower() in x.lower()
           for x in dict_.AffectedProduct], 'AffectedProduct'] = 'NON TECHNICAL ISSUE'

print("Dictionary loaded and prepared.")

#______________________________________________________________________________________________________________________#
# Loading the extracted data from the log and preparing/reshaping the data
# Extracted log data should have at least ***five*** columns for Symptom, AffectedProduct, Component, Issue, and
# Agent IDs.
print('\n', '-'*100)
print("Loading the extracted/prepared file from the log data (by previous pipeline), and preparing it for New Symptom "\
      "Detection pipeline ...")

logData_extr = pd.read_csv(LOG_EXTRACTED_ADDRESS)

# Just in case (removing null values)
logData_extr = logData_extr.loc[[pd.notnull(x) for x in logData_extr[SYMPTOM_COLUMN]], :]
logData_extr = logData_extr.loc[[pd.notnull(x) and len(x) > 0 for x in logData_extr['AffectedProduct']], :]

# Adding a new column to the extracted log data for cleaned symptoms. Cleaning is done using the filter function in the
# filters module of Support package.
filterFunc = filter_().filterSentence
logData_extr[CLEANED_SYMPTOM] = [' '.join(filterFunc(symp)).strip() for symp in logData_extr[SYMPTOM_COLUMN]]

# Just in case (removing rows with null values for cleaned symptoms)
logData_extr = logData_extr.loc[[pd.notnull(x) and len(x) > 0 for x in logData_extr[CLEANED_SYMPTOM]], :]

# Adding word count column for later filtering
logData_extr['wordCnt(cleaned)'] = [len(w.strip().split()) for w in logData_extr[CLEANED_SYMPTOM]]

# Saving the post processed file
logData_extr.to_csv(DEST_LOG_EXTRACTED_POSTPROCESSED, index=False)

# *** THIS LINE IS ADDED BASED ON THE KEVIN WOO'S RECOMMENDATION ON THROWING OUT THE LINES WITH CORRUPTED (NON-ASCII)
# CHARACTERS IN THE SYMPTOMS. IGNORING THIS LINE WILL HAVE NO EFFECT ON THE OUTPUT OTHER THAN INCLUDING FILTERED
# FORMS OF THESE SYMPTOMS IN ANALYSIS AND POSSIBLY FINAL RESULTS
logData_extr = logData_extr.loc[[len(re.findall(r'[^\x00-\x7F]+', s)) == 0 for s in logData_extr.Symptoms], :]

print("The extracted data from the log is loaded and ready for starting the New Symptom Detection pipeline.")

#______________________________________________________________________________________________________________________#
# Loading the trained model for finding similarities.
print('\n', '-'*100)
print("Loading previously trained NLP model by the Support package ... ")

TrainedModelAddress = TRAINED_MODEL_ADDRESS
supportInstance_ = Support_final.Support(threadsSourceFolder='',
                                         threadsDestFile='',
                                         documentsSourceFolder='',
                                         documentsDestFile='',
                                         allDataFile='',
                                         isModelTrained=True,
                                         modelType='doc2vec',
                                         trainedModelAddress=TrainedModelAddress,
                                         trainedDictAddress='',
                                         trainingData='',
                                         tags='',
                                         isArrayFiltered=False,
                                         trainingDataAddress='',
                                         tagSeparator=None,
                                         contentSeparator=None,
                                         isDataFiltered=False,
                                         isXmlTextExtracted=True)

print("Model loaded.")

#______________________________________________________________________________________________________________________#
# Preprocessing the log data for eliminating disqualified candidates and shrinking the size of the data
BLACK_LIST = set([x.strip().lower() for x in
                  "3RD-PARTY SOFTWARE ::: 3rd-Party Software ::: Airport Express 802.11n (2nd Generation) ::: " \
                  "Apple Pencil ::: APPLE REMOTE DESKTOP 2.0 ::: Apple TV (4th Generation) ::: APPLE WATCH 38MM ::: " \
                  "Apple Watch 42mm ::: Apple Watch Edition 38mm ::: Apple Watch Edition 42mm ::: Apple Watch Hermes" \
                  " 38mm ::: Apple Watch Hermes 42mm ::: APPLE WATCH SPORT 38MM ::: APPLE WATCH SPORT 42MM ::: ICLOUD" \
                  " ::: IMAC (21.5-INCH, LATE 2009) ::: IMAC (21.5-INCH, LATE 2012) ::: IMAC (21.5-INCH, MID 2011)" \
                  "::: IMAC (27-INCH, LATE 2012) ::: IMAC (27-INCH, MID 2010) ::: iMac (Retina 4K, 21.5-inch, Late " \
                  "2015) ::: iMac (Retina 5K, 27-inch, Late 2015) ::: IPAD ::: IPAD (3RD GEN) WI-FI ::: IPAD (3RD " \
                  "GEN) WI-FI + CELLULAR ::: IPAD (3RD GEN) WI-FI + CELLULAR (VZ) ::: IPAD (3RD GENERATION) WI-FI " \
                  "::: IPAD (3RD GENERATION) WI-FI + CELLULAR ::: IPAD (3RD GENERATION) WI-FI + CELLULAR (VZ) ::: " \
                  "IPAD (4TH GEN) WI-FI ::: IPAD (4TH GEN) WI-FI + CELLULAR ::: IPAD (4TH GEN) WI-FI + CELLULAR (MM)" \
                  " ::: IPAD 2 ::: IPAD 2 3G ::: IPAD 2 3G (VERIZON) ::: iPad 2 Wi-Fi ::: IPAD 3G ::: IPAD AIR 2 " \
                  "WI-FI ::: IPAD AIR 2 WI-FI ::: iPad Air 2 Wi-FiCustomer has Find My iPhone enabled ::: IPAD AIR " \
                  "2 WIFI, CELLULAR ::: IPAD AIR 2 WIFI, CELLULAR ::: IPAD AIR WI-FI ::: IPAD AIR WI-FI, CELLULAR " \
                  "::: IPAD MINI (RETINA) WI-FI ::: IPAD MINI (RETINA) WI-FI, CELLULAR ::: iPad mini 2 Wi-Fi ::: " \
                  "iPad mini 2 Wi-Fi, Cellular ::: IPAD MINI 3 WI-FI ::: iPad Mini 3 Wi-Fi, Cellular ::: iPad mini " \
                  "4 Wi-Fi ::: iPad mini 4 Wi-Fi, Cellular ::: IPAD MINI WI-FI ::: IPAD MINI WI-FI + CELLULAR ::: " \
                  "IPAD MINI WI-FI + CELLULAR (MM) ::: IPAD MINI WI-FI, CELLULAR ::: IPAD MINI WI-FI, CELLULAR (MM)" \
                  " ::: iPad Pro 12.9-inch Wi-Fi ::: iPad Pro 12.9-inch Wi-Fi, Cellular ::: iPhone ::: IPHONE 3GS (" \
                  "8GB) ::: IPHONE 4 ::: IPHONE 4 (8GB) ::: IPHONE 4 CDMA ::: IPHONE 4 CDMA (8GB) ::: IPHONE 4S ::: " \
                  "IPHONE 4S (8GB) ::: IPHONE 5 ::: IPHONE 5C ::: iPhone 5s ::: IPHONE 6 ::: IPHONE 6 PLUS :::" \
                  " iPhone 6s ::: iPhone 6s Plus ::: iPhone Configuration Utility (Mac) ::: IPHOTO '11 ::: iPhoto " \
                  "for iOS 2.0 ::: iPod nano (7th generation) ::: IPOD TOUCH ::: IPOD TOUCH (3RD GENERATION) ::: " \
                  "iPod touch (4th generation Late 2011) ::: IPOD TOUCH (4TH GENERATION) ::: IPOD TOUCH (5TH " \
                  "GENERATION) ::: ITUNES 10.X ::: ITUNES 11.X ::: ITUNES 12.X ::: ITUNES STORE ::: Keynote For iOS " \
                  "::: KEYNOTE FOR IOS 2.0 ::: Mac OS X 10.6.X ::: MAC OS X 10.8.X ::: MacBook Pro (13-inch Mid " \
                  "2009) ::: MACBOOK PRO (13-INCH, LATE 2011) ::: MACBOOK PRO (13-INCH, MID 2012) ::: MACBOOK PRO " \
                  "(15-INCH, LATE 2008) ::: MACBOOK PRO (RETINA, 13-INCH, LATE 2013) ::: MACBOOK PRO (RETINA, 15-" \
                  "INCH, LATE 2013) ::: NON TECHNICAL ISSUE ::: Numbers  3.0 ::: NUMBERS FOR IOS ::: OS X MAVERICKS" \
                  " 10.9 ::: OS X YOSEMITE 10.10 ::: Pages For iOS ::: PAGES FOR IOS 2.0 ::: Time Capsule ::: WATCH " \
                  "SPORT 38MM ::: Apple Watch Sport 42mm ::: iPad Pro 9.7-inch WiFi ::: iPad Pro 9.7-inch WiFi, " \
                  "Cellular ::: iPhone SE ::: IPOD TOUCH (6TH GENERATION) ::: WATCH SPORT 42MM ::: Apple Store " \
                  "3rd-Party Products ::: Apps ::: iPad 2 3G Verizon ::: iPad Pro 12.9-inch Smart Keyboard ::: " \
                  "iPad Pro 9.7-inch Smart Keyboard ::: iPad Pro 9.7-inch Wi-Fi ::: iPad Pro 9.7-inch Wi-Fi, " \
                  "Cellular ::: iPhone 6s Smart Battery Case ::: MACBOOK PRO (RETINA, 13-INCH,EARLY 2015) ::: " \
                  "Photos ::: Siri Remote ::: Apple ID ::: iPhone ::: iPad ::: iPod ::: iPad Mini ::: MacBook :::" \
                  " Apple Watch ::: IMAC ::: ipad air ::: ipad pro ::: ipod nano ::: iphone 3g ::: macbook pro :::" \
                  "macbook air ::: apple tv ::: Apple Watch Sport ::: 3rd party ::: 3rd-Party Software ::: " \
                  "third party ::: airport ::: safari ::: finder ::: keynote ::: itunes ::: itune ::: keychain " \
                  "::: imovie ::: OS X El Capitan ::: mac pro".split(":::")])
def blacklistFilter(x):
    return sum([x.lower().strip() in y for y in BLACK_LIST]) == 0

# 1. Finding the frequencies of the cleaned symptoms in log and eliminating the ones that are less than
# FREQUENCY_THRESHOLD (This value will be calculated in the next part in more details, this section is just for reducing
# the size of the data to be processed in the next step and increasing the efficiency.
sympFreq = defaultdict(lambda: 0)
for symp in logData_extr[CLEANED_SYMPTOM]:
    sympFreq[symp] += 1
rows_toKeep = [sympFreq[symp] >= FREQUENY_THRESHOLD for symp in logData_extr[CLEANED_SYMPTOM]]
logData_extr = logData_extr.loc[rows_toKeep, :]

# 2. Removing the symptoms that are in the black list
rows_toKeep = [blacklistFilter(x) for x in logData_extr[CLEANED_SYMPTOM]]
logData_extr = logData_extr.loc[rows_toKeep, :]

#______________________________________________________________________________________________________________________#
# Measuring the time dependent variations for frequencies of symptoms and P-C-I combinations
print('\n', '-'*100)
print("Measuring the time variations for the frequency of symptoms in the log by increasing level of granularity "\
      "(and merging the results):\n"\
      "1. Cleaned symptoms \n"\
      "2. Cleaned symptoms in the log per CI group \n" \
      "3. Cleaned symptoms in the log per PCI group "
      )

START = time()

logData_extr['startDate'] = [x.split()[0] for x in logData_extr[TIME_COLUMN]]

def groupKey_timeChange(data_, keys=[]):
    # This function gets a data_ table of extracted log data, and calculates the aggregate frequencies of filtered
    # symptoms, the numbers of agents involved in for each symptom inside the time interval tha is used by the groupby.
    # *** keys should be either none or names of the columns in the dictionary, and name of the key that is used for
    # grouping on the log data.

    # Variables to be returned:
    cleanedSymp = []
    cleanedSympFreqs = []
    cleanedSympNumUniqueAgents = []
    cleanedSympAgents = []

    # Finding and saving the agent ids involved in generating symptom (cleaned).
    uniqueSympsAgents = {}
    for i, symp in enumerate(data_[CLEANED_SYMPTOM]):
        if symp not in uniqueSympsAgents:
            uniqueSympsAgents[symp] = defaultdict(lambda: 0)

        if pd.isnull(data_[AGENT_COLUMN].iloc[i]):
            continue

        agents_ = str(data_[AGENT_COLUMN].iloc[i]).split(',')
        for agent_ in agents_:
            uniqueSympsAgents[symp][agent_] += 1

    # For each symptom: finding the frequency of symptom in this group, as well as, the numbers of agents involved (
    # and saving the agents ids.
    for symp in uniqueSympsAgents:
        cleanedSymp.append(symp)
        cleanedSympFreqs.append(sum(uniqueSympsAgents[symp].values()))
        cleanedSympNumUniqueAgents.append(len(uniqueSympsAgents[symp].keys()))
        cleanedSympAgents.append(', '.join([str(x) + ' (' + str(y) + ')' for x,y in uniqueSympsAgents[symp].items()]))

    if len(keys) == 0:
        suffix_ = ''
    else:
        suffix_ = '_'.join(keys)

    return pd.DataFrame({'startDate': [list(data_.startDate)[0]] * len(cleanedSymp),
                         CLEANED_SYMPTOM: cleanedSymp,
                         'FrequencyOfCleanedSymptom_' + suffix_: cleanedSympFreqs,
                         'NumUniqueAgentsInCleanedSymptom_' + suffix_: cleanedSympNumUniqueAgents,
                         'AgentsTypedSymptom_' + suffix_: cleanedSympAgents})

keys1 = [CLEANED_SYMPTOM]
g = logData_extr.groupby(['startDate'] + keys1)
print("\n1. Cleaned symptoms/Day groups (numbers of groups to aggregate: %s)" % len(g.groups))
data1_ = progress(g, groupKey_timeChange, ['startDate'])
data1_.reset_index(drop=True, inplace=True)

keys2 = [COMPONENT_COLUMN, ISSUE_COLUMN]
g = logData_extr.groupby(['startDate'] + keys2)
print("\n2. Component-Issue/Day groups (numbers of groups to aggregate: %s)" % len(g.groups))
data2_ = progress(g, groupKey_timeChange, ['startDate'] + keys2)
data2_.drop('startDate', inplace=True, axis=1)
data2_.reset_index(drop=False, inplace=True)

print("\n3. ...")
keys3 = [PRODUCT_COLUMN, COMPONENT_COLUMN, ISSUE_COLUMN]
g = logData_extr.groupby(['startDate'] + keys3)
print("\n3. Product-Component-Issue/Day groups (numbers of groups to aggregate: %s)" % len(g.groups))
data3_ = progress(g, groupKey_timeChange, ['startDate'] + keys3)
data3_.drop('startDate', inplace=True, axis=1)
data3_.reset_index(drop=False, inplace=True)

# Merging the results with the main data
mergedSims_ = pd.merge(data2_, data1_, on=['startDate'] + keys1)
mergedSims_ = pd.merge(data3_, mergedSims_, on=['startDate'] + keys1 + keys2)
logData_timeChange = pd.merge(logData_extr, mergedSims_, on=['startDate'] + keys1 + keys3)

# Adding a column for total volume of data per date (day) for calculating the relative frequency
TOTAL_VOlUME = data1_.groupby('startDate').apply(lambda x:
                                                 pd.DataFrame({'TotalVolumePerDay':
                                                                   [sum(x['FrequencyOfCleanedSymptom_startDate'])]}))
TOTAL_VOlUME.reset_index(drop=False, inplace=True)
logData_timeChange = pd.merge(logData_timeChange, TOTAL_VOlUME[['startDate', 'TotalVolumePerDay']], on='startDate')
logData_timeChange['RelatingFrequencyPerDay[%]'] = [x / y * 100 for x, y in
                                                 zip(logData_timeChange.FrequencyOfCleanedSymptom_startDate,
                                                     logData_timeChange.TotalVolumePerDay)]

# Adding the velocities and accelerations of the frequencies of the cleaned symptoms for the defined groups


# Selecting columns and reshaping the data
COLUMNS_TO_KEEP = ['startDate', 'Symptoms', 'cleanedSymptoms', 'AffectedProduct', 'CaseIssue', 'Component', 'agentID',
                   'FrequencyOfCleanedSymptom_startDate_AffectedProduct_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_startDate_AffectedProduct_Component_CaseIssue',
                   'AgentsTypedSymptom_startDate_AffectedProduct_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_startDate_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_startDate_Component_CaseIssue',
                   'AgentsTypedSymptom_startDate_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_startDate',
                   'NumUniqueAgentsInCleanedSymptom_startDate',
                   'AgentsTypedSymptom_startDate',
                   'TotalVolumePerDay',
                   'RelatingFrequencyPerDay[%]']
logData_timeChange = logData_timeChange[COLUMNS_TO_KEEP]

# Saving the results
logData_timeChange.to_csv(DEST_ADDRESS_LOG_FREQ_BY_TIME, index=False)

END = time()
print("\nMeasuring the time variations of frequencies finished. Time spent: %s minutes." % str(round((END - START)/60,
                                                                                                     2)))

#______________________________________________________________________________________________________________________#
# Finding the similarities as well as frequencies and agents roles for the symptoms in log (for groups of various
# granularity)
def groupKey_allTimesDictCompare(data_, keys=[], modelInstance = None, filterFunc = filterFunc):
    # This function gets a data_ table of extracted log data, and calculates the aggregate frequencies of filtered
    # symptoms, the numbers of agents involved in for each symptom, and finally it finds the most similar
    # (and measures the similarity to) symptom in the dictionary for the defined group by the keys.
    # *** if keys is left None, whole dictionary will be used.
    # *** keys should be either none or names of the columns in the dictionary, and name of the key that is used for
    # grouping on the log data.

    # Trained model
    modelInstance = modelInstance

    # Variables to be returned:
    cleanedSymp = []
    cleanedSympFreqs = []
    cleanedSympNumUniqueAgents = []
    cleanedSympAgents = []
    mostSimilarSymp = []
    maxSimilarity = []
    areAllWordsIn = []

    # Finding and saving the agent ids involved in generating symptom (cleaned).
    uniqueSympsAgents = {}
    for i, symp in enumerate(data_[CLEANED_SYMPTOM]):
        if symp not in uniqueSympsAgents:
            uniqueSympsAgents[symp] = defaultdict(lambda: 0)

        if pd.isnull(data_[AGENT_COLUMN].iloc[i]):
            continue

        agents_ = str(data_[AGENT_COLUMN].iloc[i]).split(',')
        for agent_ in agents_:
            uniqueSympsAgents[symp][agent_] += 1

    # Finding the most similar symptom in the dictionary (selected by the keys used for grouping) to the cleaned
    # symptoms.
    dictSymptomsInGrp = None
    if len(keys) == 0:
        dictSymptomsInGrp = list(set(dict_['Symptoms']))
    else:
        indDictSelect = [True] * dict_.shape[0]
        for key in keys:
            # For each key involved, limit the numbers of selectable symptoms from the dictionary.
            keyVal = list(data_[key])[0]
            indDictSelect = [x and y for x, y in zip(dict_[key] == keyVal, indDictSelect)]

        dictSymptomsInGrp = list(set(dict_['Symptoms'].loc[indDictSelect]))

    # Calculating the feature vectors for the selected dictionary symptoms using the loaded model instance.
    # If there is no key provided, means that whole symptoms in the dictionary (step 1) will be used.
    # The passed model object for step 1 already have calculated vectors.
    if len(dictSymptomsInGrp) > 0 and len(keys) > 0:
        modelInstance.getFeatureVectors(textFileAddress='',
                                        textArray=dictSymptomsInGrp,
                                        tagSeparator=None,
                                        tags=dictSymptomsInGrp,
                                        contentSeparator=None,
                                        isFileFiltered=False,
                                        isArrayFiltered=False,
                                        isFeatureVectorsAvailable=False,
                                        featureVecsAddress='',
                                        destAddress='')

    # For each symptom: finding the frequency of symptom in this group, as well as, the numbers of agents involved (
    # and saving the agents ids. Then, finding the most similar symptom in the selected dictionary symptoms to the
    # current symptom.
    for symp in uniqueSympsAgents:
        cleanedSymp.append(symp)
        cleanedSympFreqs.append(sum(uniqueSympsAgents[symp].values()))
        cleanedSympNumUniqueAgents.append(len(uniqueSympsAgents[symp].keys()))
        cleanedSympAgents.append(', '.join([str(x) + ' (' + str(y) + ')' for x,y in uniqueSympsAgents[symp].items()]))

        if len(dictSymptomsInGrp) == 0:
            # If no symptom under current group is found in the dictionary.
            mostSimilarSymp.append(np.nan)
            maxSimilarity.append(np.nan)
            areAllWordsIn.append(np.nan)
            continue

        symp = str(symp)
        mostSimilar = supportInstance_.similars(symp, maxSimilars=min(5, len(dictSymptomsInGrp)))
        mostSimilarSymp += [mostSimilar[0][0]]
        maxSimilarity += [mostSimilar[0][1]]
        areAllWordsIn += [True]  # Since similarity score may not be sufficient detecting shorter queries
        for word in symp.strip().lower().split():
            if word not in filterFunc(mostSimilarSymp[-1])[-1]:
                areAllWordsIn[-1] = False
                break

    if len(keys) == 0:
        suffix_ = ''
    else:
        suffix_ = '_'.join(keys)
    return pd.DataFrame({CLEANED_SYMPTOM: cleanedSymp,
                         'FrequencyOfCleanedSymptom_' + suffix_: cleanedSympFreqs,
                         'NumUniqueAgentsInCleanedSymptom_' + suffix_: cleanedSympNumUniqueAgents,
                         'AgentsTypedSymptom_' + suffix_: cleanedSympAgents,
                         'MostSimilarSymp_' + suffix_: mostSimilarSymp,
                         'MaxSimilarity_' + suffix_: maxSimilarity,
                         'AreAllWordsIn_' + suffix_: areAllWordsIn})

# Finding most similar symptom in the dictionary
print('\n', '-'*100)
print("Finding the most similar symptoms in the dictionary for each symptom in the log by increasing level of\n"\
      "granularity (and merging the results): \n"\
      "1. Cleaned symptoms in the log against all symptoms in the dictionary. \n"\
      "2. Cleaned symptoms in the log per CI group against symptoms in the dictionary for the CI group (if found any)."\
      "\n" \
      "3. Cleaned symptoms in the log per PCI group against symptoms in the dictionary for the PCI group (if found "\
      "any)."
      )

START = time()

# Finding most similar symptoms in the dictionary for the queries in the log data and joining data
# To prevent model calculations at each grouping, since all the groups use the same set of symptoms (all) in the
# dictionary, the vectors are obtained outside and passed to the apply function.
dictSymptomsInGrp = list(set(dict_['Symptoms']))
supportInstance_.getFeatureVectors(textFileAddress='',
                                   textArray=dictSymptomsInGrp,
                                   tagSeparator=None,
                                   tags=dictSymptomsInGrp,
                                   contentSeparator=None,
                                   isFileFiltered=False,
                                   isArrayFiltered=False,
                                   isFeatureVectorsAvailable=False,
                                   featureVecsAddress='',
                                   destAddress='')

keys1 = [CLEANED_SYMPTOM]
g = logData_extr.groupby(keys1)
print("\n1. Cleaned symptoms groups (numbers of groups to aggregate: %s)" % len(g.groups))
data1_ = progress(g, groupKey_allTimesDictCompare, [], supportInstance_)
data1_.reset_index(drop=True, inplace=True)

keys2 = [COMPONENT_COLUMN, ISSUE_COLUMN]
g = logData_extr.groupby(keys2)
print("\n2. Component-Issue groups (numbers of groups to aggregate: %s)" % len(g.groups))
data2_ = progress(g, groupKey_allTimesDictCompare, keys2, supportInstance_)
data2_.reset_index(drop=False, inplace=True)

keys3 = [PRODUCT_COLUMN, COMPONENT_COLUMN, ISSUE_COLUMN]
g = logData_extr.groupby(keys3)
print("\n3. Product-Component-Issue groups (numbers of groups to aggregate: %s)" % len(g.groups))
data3_ = progress(g, groupKey_allTimesDictCompare, keys3, supportInstance_)
data3_.reset_index(drop=False, inplace=True)

# Merging the results with the main data
mergedSims_ = pd.merge(data2_, data1_, on=keys1)
mergedSims_ = pd.merge(data3_, mergedSims_, on=keys1 + keys2)
logData_sims = pd.merge(logData_extr, mergedSims_, on=keys1 + keys3)
COLUMNS_TO_KEEP = ['Symptoms', CLEANED_SYMPTOM, 'AffectedProduct', 'CaseIssue', 'Component', 'agentID',
                   'MaxSimilarity_AffectedProduct_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_AffectedProduct_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_AffectedProduct_Component_CaseIssue',
                   'AgentsTypedSymptom_AffectedProduct_Component_CaseIssue',
                   'AreAllWordsIn_AffectedProduct_Component_CaseIssue',
                   'MostSimilarSymp_AffectedProduct_Component_CaseIssue',
                   'MaxSimilarity_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_Component_CaseIssue',
                   'AgentsTypedSymptom_Component_CaseIssue',
                   'AreAllWordsIn_Component_CaseIssue',
                   'MostSimilarSymp_Component_CaseIssue',
                   'MaxSimilarity_',
                   'FrequencyOfCleanedSymptom_',
                   'NumUniqueAgentsInCleanedSymptom_',
                   'AgentsTypedSymptom_',
                   'AreAllWordsIn_',
                   'MostSimilarSymp_',
                   'wordCnt(cleaned)']
logData_sims = logData_sims[COLUMNS_TO_KEEP]

# del logData_extr  # Freeing some memory

# Saving the results
logData_sims.to_csv(DEST_ADDRESS_LOG_DICT_SIMS, index=False)

END = time()
print("\nSimilar symptoms per defined groups found. Time spent: %s minutes." % str(round((END - START)/60, 2)))

#______________________________________________________________________________________________________________________#
# Selecting the new symptom candidates based on the defined thresholds above
print('\n', '-'*100)
print("Selecting new symptom candidates based on the defined thresholds and preparing the results.")

# Replacing the cosine similarity of the non-existent PCI cases in the dictionary (put nan above) with the ones measured
# for the CI groups, and zero otherwise.
logData_sims['MaxSimilarity_AffectedProduct_Component_CaseIssue'] = [
    cos_pci if not pd.isnull(cos_pci) else cos_ci for cos_pci, cos_ci in
    zip(logData_sims['MaxSimilarity_AffectedProduct_Component_CaseIssue'],
        logData_sims['MaxSimilarity_Component_CaseIssue'])]

# Filling the similarities for the non-existent categories to zero.
logData_sims['MaxSimilarity_AffectedProduct_Component_CaseIssue'].fillna(0, inplace=True)
logData_sims['MaxSimilarity_Component_CaseIssue'].fillna(0, inplace=True)

# Selecting candidates based on the defined thresholds (SEE HEADER FOR THRESHOLDS)
logSims_select = logData_sims.loc[[pciSim < PCIGRP_SIMILARITY_THRESHOLD and
                                   ciSim < CIGRP_SIMILARITY_THRESHOLD and
                                   allSim < ALL_SIMILARITY_THRESHOLD and
                                   numAgents > NUM_AGENTS_THRESHOLD and
                                   not allWordsIn
                                   for pciSim, ciSim, allSim, numAgents, allWordsIn in
                                   zip(logData_sims['MaxSimilarity_AffectedProduct_Component_CaseIssue'],
                                       logData_sims['MaxSimilarity_Component_CaseIssue'],
                                       logData_sims['MaxSimilarity_'],
                                       logData_sims['NumUniqueAgentsInCleanedSymptom_'],
                                       logData_sims['AreAllWordsIn_'])], :]

# Saving the results
logSims_select.to_csv(DEST_ADDRESS_NEWSYMP_SELECTED_CANDIDATES, index=False)

#______________________________________________________________________________________________________________________#
# Removing the repeated/included symptom in each PCI group and then clustering/selecting the longest symptoms within
# each cluster for each PCI
def areAllWordsIn(sent1, sent2):
    # Checking if all words in sent1 are in sent2
    words1 = [w.strip() for w in sent1.strip().split()]
    words2 = set([w.strip() for w in sent2.strip().split()])
    for w in words1:
        if w not in words2:
            return False
    return True
def clusterSympsInclusionCheck(x, max_d=0.2):
    # This function clusters the symptoms in the passed section of the data frame for each PCI group and chooses one
    # row for each cluster.
    # It first sorts the input dataframe by the 'filteredSympWordCnt' column (shorter symptoms first), then checks
    # if any of the shorter symptoms are in included in the longer ones below it(just word by word checking, no order
    # is checked here), and excludes the rows with sorter messages
    # Then it does clustering based on the 'max_d' and chooses the longest symptom within each cluster.

    # Selecting symptoms that are not included in others
    N = x.shape[0]
    rowsToUse = []
    x = x.sort_values('wordCnt(cleaned)')  # DO NOT USE INPLACE HERE, IT USES INPLACE MEMORY FOR ALL ITERATIONS!!!!
    filtSymps = list(x['cleanedSymptoms'])
    for i, filtSymp in enumerate(filtSymps):
        isIn = False
        if pd.isnull(filtSymp): continue
        for j in range(i+1, N):
            if pd.isnull(filtSymps[j]): continue
            if areAllWordsIn(filtSymp, filtSymps[j]):
                isIn = True
                break
        if not isIn:
            rowsToUse.append(i)
    x = x.iloc[rowsToUse, :]

    if x.shape[0] <= 1:
        x['Cluster'] = 1
        return x

    # Finding the feature vectors for clustering
    supportInstance_.getFeatureVectors(textFileAddress='',
                                   textArray=list(x['Symptoms']), tagSeparator=None,
                                   tags=list(x['Symptoms']),
                                   contentSeparator=None,
                                   isFileFiltered=False,
                                   isArrayFiltered=False,
                                   isFeatureVectorsAvailable=False,
                                   featureVecsAddress='',
                                   destAddress='')

    # Getting feature vectors
    vecs = [x[1] for x in list(supportInstance_.featureVectorsClass)]

    # Cluster analysis
    # Z_euclid = linkage(vecs, method='ward')
    Z_cosine = linkage(vecs, method='average', metric='cosine')
    Z = Z_cosine

    # Getting clusters
    x['Cluster'] = fcluster(Z, max_d, criterion='distance')
    x.sort_values(['Cluster'], inplace=True)
    x.sort_values(['wordCnt(cleaned)'], ascending=False, inplace=True)

    return pd.DataFrame(x)

g = logSims_select.groupby(['AffectedProduct', 'Component', 'CaseIssue'])
logSims_selectFinal = progress(g, clusterSympsInclusionCheck)
logSims_selectFinal.reset_index(drop=True, inplace=True)

COLUMNS_TO_KEEP_ = ['Symptoms', 'cleanedSymptoms', 'AffectedProduct', 'CaseIssue', 'Component',
                   'MaxSimilarity_AffectedProduct_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_AffectedProduct_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_AffectedProduct_Component_CaseIssue',
                   'AgentsTypedSymptom_AffectedProduct_Component_CaseIssue',
                   'AreAllWordsIn_AffectedProduct_Component_CaseIssue',
                   'MostSimilarSymp_AffectedProduct_Component_CaseIssue',
                   'MaxSimilarity_Component_CaseIssue',
                   'FrequencyOfCleanedSymptom_Component_CaseIssue',
                   'NumUniqueAgentsInCleanedSymptom_Component_CaseIssue',
                   'AgentsTypedSymptom_Component_CaseIssue',
                   'AreAllWordsIn_Component_CaseIssue',
                   'MostSimilarSymp_Component_CaseIssue',
                   'MaxSimilarity_',
                   'FrequencyOfCleanedSymptom_',
                   'NumUniqueAgentsInCleanedSymptom_',
                   'AgentsTypedSymptom_',
                   'AreAllWordsIn_',
                   'MostSimilarSymp_',
                   'wordCnt(cleaned)',
                    'Cluster']
logSims_selectFinal = logSims_selectFinal[COLUMNS_TO_KEEP_]

# Saving the results
logSims_selectFinal.to_csv(DEST_ADDRESS_NEWSYMP_SELECTED_CANDIDATES_, index=False)

# Selecting just the first (longest) symptom among similar cleaned symptoms in a cluster
logSims_selectFinal.drop_duplicates(['Cluster', 'AffectedProduct', 'Component', 'CaseIssue'], inplace=True)

# Choosing representative symptoms, for the symptoms with the same cleaned form, based on the frequency of symptom
# per agent (if the first choice is one word the second longer that includes will be chosen)
sympPresentation = {}
for symp in set(logSims_selectFinal.cleanedSymptoms):
    candidates_ = logSims_select[logSims_select.cleanedSymptoms == symp]
    data_ = candidates_.groupby('Symptoms').apply(lambda x: pd.DataFrame({'frq': [x.shape[0]],
                                                                          'numAg': [len(set(x.agentID))]}))
    data_.reset_index(inplace = True)
    data_['freqPerAgent'] = [f/n for f, n in zip(data_.frq, data_.numAg)]
    data_['numWords'] = [len(x.strip().split()) for x in data_['Symptoms']]

    # Sorting by the frequencies and checking if the first choice is one word included in the next best choice
    # If this is the case, the second best will be chosen
    data_.sort_values('freqPerAgent', ascending=False, inplace=True)
    moreThanOneWord = data_.Symptoms.loc[data_.numWords > 1]
    if len(moreThanOneWord) > 0:
        sympPresentation[symp] = moreThanOneWord.iloc[0]
    else:
        sympPresentation[symp] = data_.Symptoms.iloc[0]
logSims_selectFinal.loc[:, 'ORIGINAL SYMPTOM'] = [sympPresentation[s] for s in logSims_selectFinal.cleanedSymptoms]

# Doing a very cautious clustering to capture the symptoms that have almost the same shape but with slight semantic
# difference (such as word ordering), as a final step in uniforming the symptom presentations.
sympsToCluster = pd.DataFrame(logSims_selectFinal['ORIGINAL SYMPTOM'])
sympsToCluster.drop_duplicates(inplace=True)
supportInstance_.getFeatureVectors(textFileAddress='',
                                   textArray=list(sympsToCluster['ORIGINAL SYMPTOM']), tagSeparator=None,
                                   tags=list(sympsToCluster['ORIGINAL SYMPTOM']),
                                   contentSeparator=None,
                                   isFileFiltered=False,
                                   isArrayFiltered=False,
                                   isFeatureVectorsAvailable=False,
                                   featureVecsAddress='',
                                   destAddress='')
vecs = [x[1] for x in list(supportInstance_.featureVectorsClass)]
Z_cosine = linkage(vecs, method='average', metric='cosine')
Z = Z_cosine
MAX_D = 0.05
sympsToCluster['Cluster'] = fcluster(Z, MAX_D, criterion='distance')
sympsSelect = sympsToCluster.groupby('Cluster').apply(lambda x: x.iloc[0, :])
sympsSelect.rename(columns={'ORIGINAL SYMPTOM':'selectedSymp'}, inplace=True)
sympsToCluster = pd.merge(sympsSelect, sympsToCluster, on='Cluster')

logSims_selectFinal = pd.merge(sympsToCluster, logSims_selectFinal, on='ORIGINAL SYMPTOM')
logSims_selectFinal.drop('ORIGINAL SYMPTOM', axis=1, inplace=True)
logSims_selectFinal.rename(columns={'selectedSymp': 'ORIGINAL SYMPTOM'}, inplace=True)

# Saving the results for final NSD reformatting pipeline
logSims_selectForFinalStep = logSims_selectFinal[['Symptoms', 'ORIGINAL SYMPTOM', 'cleanedSymptoms',
                                                  'AffectedProduct', 'Component', 'CaseIssue']]
logSims_selectForFinalStep['ORIGINAL SYMPTOM'] = [re.sub(r'[^\x00-\x7F]+', '', s) for s in
                                                  logSims_selectForFinalStep['ORIGINAL SYMPTOM']]
logSims_selectForFinalStep.to_csv(DEST_ADDRESS_NEWSYMP_FOR_FINAL_STEP, index=False)

# Saving the Original Symptoms for Kevin-Saurav's pipeline for reformatting the symptoms
origSymps = pd.DataFrame(logSims_selectForFinalStep['ORIGINAL SYMPTOM'])
origSymps.drop_duplicates(inplace=True)
origSymps.to_csv(DEST_ADDRESS_SYMPTOMS_FOR_REFORMATTING, index=False)

#______________________________________________________________________________________________________________________#
ALL_END = time()

print('\n', '-'*100)
print("Process finished. Total time spent: %s minutes.\n" % str(round((ALL_END - ALL_START)/60, 2)))
