#!/usr/bin/env python3

#______________________________________________________________________________________________________________________#
## codes for extracting required information out of the log data

# LOG DATA EXAMPLES:
#
# symptom log file
# columns:
# source	start_timestamp	requesttype	locale	query	end_timestamp
# requestid	traceid	request_data	response_data	year	month
#
# request_data:
# {"requestId":"C70EE901-8EF0-0001-5792-1FE3212D148C","customerCountry":"USA",
# "eligibleProductId":"500016","limit":"5","locale":"en_US","productEligibility":"Y",
# "purchaseDate":"2015-10-02","query":"Liquid Damage","requestType":"SYMPTOM",
# "productGroupFamilyId":"PGF31005","productGroupId":"421","affectedProductId":"",
# "agentId":"871059339","timestamp":1462592691000,"testId":"pAXOjkJRSTWX9o-mWqJxcg",
# "start_timestamp":1462592555973,"X-CG-APP-DSID":"789","X-CG-ACCESS-KEY":
# "c0510d2616f81bdb08fea8d648143c367f98076b96ba98829002cd285e6684d3","X-CG-AUTH-TOKEN":""}
#
# response_data:
# {"testId":"pAXOjkJRSTWX9o-mWqJxcg","requestId":"C70EE901-8EF0-0001-5792-1FE3212D148C",
# "suggestions":[{"description":"Customer has a damaged device and is calling Apple to find out
# what options they have for a repair or replacement. The customer may or may not have AppleCare or
# AppleCare+.","query":"Damage: Liquid Damage","symptomIndex":1},{"description":"Customer has
# questions regarding using their device.","query":"How to erase all content and settings on a
# device that will not power on","symptomIndex":2}]}
#
# classification log file
# columns:
# source	start_timestamp	requesttype	locale	query	end_timestamp
# requestid	traceid	request_data	response_data	year	month
# request_data:
# {"requestId":"C70EE902-EFE0-0001-C3B7-16E019251920","limit":"3","productGroupId":"421",
# "query":"Damage: Liquid Damage","requestType":"CLASSIFICATIONS","affectedProductId":"500016",
# "eligibleProductId":"500016","locale":"en_US","agentId":"871059339","symptomIndex":1,
# "timestamp":1462592697000,"testId":"pAXOjkJRSTWX9o-mWqJxcg","start_timestamp":1462592561636,
# "X-CG-APP-DSID":"789","X-CG-ACCESS-KEY":"c0510d2616f81bdb08fea8d648143c367f98076b96ba98829002cd285e6684d3",
# "X-CG-AUTH-TOKEN":""}
#
# response_data:
# {"testId":"pAXOjkJRSTWX9o-mWqJxcg","requestId":"C70EE902-EFE0-0001-C3B7-16E019251920","CLASSIFICATIONS":
# [{"affectedProduct":"500016","classificationIndex":1,"component":"26112B","issue":"IP122"}]}
#
# feedback log file
# columns:
# source	start_timestamp	requesttype	locale	query	end_timestamp
# requestid	traceid	request_data	response_data	year	month
#
# request_data:
# {"requestId":"C70EE90A-CB20-0001-82EA-EF931B271D04","query":"Damage: Liquid Damage","caseId":"1103957952",
# "productGroupFamilyId":"PGF31005","productGroupId":"421","classificationSet":{"affectedProduct":"iPhone 6s",
# "component":"Physical Damage","issue":"Liquid Damage"},"affectedProductId":"500016","eligibleProductId":"500016",
# "customerCountry":"USA","productEligibility":"Y","purchaseDate":"2015-10-02","locale":"en_US","agentId":"871059339",
# "classificationIndex":0,"testId":"pAXOjkJRSTWX9o-mWqJxcg","start_timestamp":1462592595672,"X-CG-APP-DSID":"789",
# "X-CG-ACCESS-KEY":"c0510d2616f81bdb08fea8d648143c367f98076b96ba98829002cd285e6684d3","X-CG-AUTH-TOKEN":"",
# "requestType":"FEEDBACK"}
#
# response_data:
# {"feedback":{"success":"true"},"requestId":"C70EE90A-CB20-0001-82EA-EF931B271D04"}


'''
Created on May 18, 2016 (revised several times afterwards)

@author: eliyarasgarieh

This file contains codes for processing extracted log data from symptom, classification, feedback tables.

Inputs:
- Address of curation dictionary (in .xlsx format)
- Address of pulled symptom files from hive
- Address of pulled classification files from hive
- Address of pulled feedback files from hive
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

'''

import pandas as pd
import numpy as np
import re
import sys, os
from time import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Recording the total run time (printed at the end)
ALL_START = time()

# Reading the command line arguments and assigning the required values related (constant) variables
args = sys.argv

SOURCE = '.'
DICT_ADDRESS = args[1]
SYMP_FILE_ADDRESS = os.path.join(SOURCE, args[2])
CLASS_FILE_ADDRESS = os.path.join(SOURCE, args[3])
FEED_FILE_ADDRESS = os.path.join(SOURCE, args[4])
MAP_CODE_DIR = args[5]
DATE_PERIOD = ''
SEP = "::-::-::"  # especial separator used since the tab and comma where hard to use due to condition of the text data
if len(args) > 6: DATE_PERIOD = args[6]
if len(args) > 7: SEP = args[7]

COMBINED_SCF_DEST = os.path.join(SOURCE, "combinedSCF_%s.csv" % DATE_PERIOD)
LOG_EXTRACTED_SCF_DEST = os.path.join(SOURCE, "logExtracted_SCF_TestIDgrps_%s.csv" % DATE_PERIOD)
LOG_EXTRACTED_SC_CF_DEST = os.path.join(SOURCE, "logExtracted_SC_CF_TestIDgrps_%s.csv" % DATE_PERIOD)
LOG_EXTRACTED_SCF_DEST_REFORM = os.path.join(SOURCE, "logExtracted_SCF_TestIDgrps_ForNSDpipeline_%s.csv" % DATE_PERIOD)
LOG_EXTRACTED_CF_DEST_REFORM = os.path.join(SOURCE, "logExtracted_CF_TestIDgrps_ForNSDpipeline_%s.csv" % DATE_PERIOD)

# Product-Component-Issue mapping codes
PROD_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "productToGroupMap_v4.0.xlsx")
COMP_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "componentMap_v4.0.xlsx")
ISSUE_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "issueMap_v4.0.xlsx")

# Initializing dictionaries for saving the non-existent cases as by product of pipeline
prodsNotFound = {'TestID': [], 'AffectedProductCode': []}
eligProdsNotFound = {'TestID': [], 'EligibleProductCode': []}
componentsNotFound = {'TestID': [], 'ProductGroupCode': [], 'ComponentCode': []}
issuesNotFound = {'TestID': [], 'ProductGroupCode': [], 'IssueCode': []}

PRODS_NOT_FOUND_DEST = "./affectedProductCodesNotFound_%s.csv" % DATE_PERIOD
COMP_NOT_FOUND_DEST = "./productGroupComponentCodesNotFound_%s.csv" % DATE_PERIOD
ISSUE_NOT_FOUND_DEST = "./productGroupIssueCodesNotFound_%s.csv" % DATE_PERIOD

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

# ______________________________________________________________________________________________________________________#
# Loading .txt log files pulled by Hive and cleaning/preparing them
# The files are extracted in the format identified by the column names.
# If the files format changes the following lines for extracting data should also change

print('\n', '-' * 100)
print("Loading S, C, and F log data and preparing/combining them ...")
START = time()

sys.stdout.write("Progress: ")
sympsColumns = [x.strip() for x in "source, requesttype, request_data, testID, requestid, traceid," \
                                   "start_timestamp, end_timestamp, start_datetime, end_datetime, timestamp_inRequestData," \
                                   "query, productGroupFamilyId, productGroupId, affectedProductId,eligibleProductId," \
                                   "agentId, symptom_suggestions, month, year".split(",")]
classColumns = [x.strip() for x in "source, requesttype, request_data, testID, start_timestamp, end_timestamp," \
                                   "start_datetime, end_datetime, timestamp_inRequestData, query, productGroupFamilyId," \
                                   "productGroupId, affectedProductId, eligibleProductId, agentId, selected_symptom," \
                                   "classification_suggestions".split(",")]
feedColumns = [x.strip() for x in "source, requesttype, request_data, testID, start_timestamp, end_timestamp," \
                                  "start_datetime, end_datetime, timestamp_inRequestData, query, productGroupFamilyId," \
                                  "productGroupId, affectedProductId, eligibleProductId, agentId, caseID," \
                                  "classificationSet, selected_classification".split(",")]

LOCAL_PATTERN = '\"locale\":\"(.*?)\"'  # Later requested by the group, just for checking that data is for 'en_US'
symps_ = pd.read_csv(SYMP_FILE_ADDRESS, header=None, sep=SEP, engine='python')
symps_.columns = sympsColumns
symps_['local'] = [re.findall(pattern=LOCAL_PATTERN, string=x)[0] for x in symps_['request_data']]
symps_.drop('request_data', axis=1, inplace=True)  # This column seems useless, and will be removed from pipeline
symps_complete = symps_.loc[[not pd.isnull(x) and x != '\\N' for x in symps_.testID], :]

class_ = pd.read_csv(CLASS_FILE_ADDRESS, header=None, sep=SEP, engine='python')
class_.columns = classColumns
class_['local'] = [re.findall(pattern=LOCAL_PATTERN, string=x)[0] for x in class_['request_data']]
class_.drop('request_data', axis=1, inplace=True)  # This column seems useless, and will be removed from pipeline
class_complete = class_.loc[[not pd.isnull(x) and x != '\\N' for x in class_.testID], :]

feed_ = pd.read_csv(FEED_FILE_ADDRESS, header=None, sep=SEP, engine='python')
feed_.columns = feedColumns
feed_['local'] = [re.findall(pattern=LOCAL_PATTERN, string=x)[0] for x in feed_['request_data']]
feed_.drop('request_data', axis=1, inplace=True)  # This column seems useless, and will be removed from pipeline
feed_complete = feed_.loc[[not pd.isnull(x) and x != '\\N' for x in feed_.testID], :]

# Combining S, C, F data
combinedSCF = pd.concat([symps_complete, class_complete, feed_complete])
combinedSCF = combinedSCF[["testID", "source", "requesttype", "start_timestamp",
                           "end_timestamp", "start_datetime", "timestamp_inRequestData",
                           "query", "productGroupFamilyId", "productGroupId", "affectedProductId",
                           "eligibleProductId", "agentId", "symptom_suggestions", "selected_symptom",
                           "classification_suggestions", "classificationSet", "selected_classification",
                           "caseID", "month", "year", "local"]]
combinedSCF.replace(to_replace='\\N', value=np.nan, inplace=True)

# Adding the duration of events for each testID and saving the extracted data from the log files
def timeFromStart(x):
    # Calculating the duration of event for each testID
    x = x.sort_values('start_timestamp')
    x['timeFromFirstAppearance[min]'] = (x.start_timestamp - list(x.start_timestamp)[0]) / 1000 / 60
    return x

g = combinedSCF.sort_values('start_timestamp').groupby('testID', sort=False)  # Using extra memory temporarily for
                                                                              # better presentation
combinedSCF = g.apply(timeFromStart)
combinedSCF.reset_index(drop=True, inplace=True)
combinedSCF.to_csv(COMBINED_SCF_DEST, index=False)
del g

END = time()
print("S, C, and F data prepared and combined. Time spent: %s minutes.\n" % str(round((END - START) / 60, 2)))

# ______________________________________________________________________________________________________________________#
# Loading the dictionary and saving dictionary's product-component-issues for the use by
# classSuggCodeExtractorTranslator function

print('\n', '-' * 100)
print("Loading/preparing the symptom-classification dictionary ... ")

dict_ = pd.read_excel(DICT_ADDRESS)
dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']] = \
    dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']].replace(np.nan, '')
dict_.loc[['NON'.lower() in x.lower() and 'TECHNICAL'.lower() in x.lower() and 'ISSUE'.lower() in x.lower()
           for x in dict_.AffectedProduct], 'AffectedProduct'] = 'NON TECHNICAL ISSUE'

print("Dictionary loaded and prepared.")

# ______________________________________________________________________________________________________________________#
# Post processing the cleaned/prepared file
print('\n', '-' * 100)
print("Starting post-processing the combined log data (SCF patterns)... ")
START = time()

# loading product-component-issue mapping codes for translating the codes in the log data
prodCodes = pd.read_excel(PROD_CODES_ADDRESS).iloc[:, [0, 1, 3]].drop_duplicates()
compCodes = pd.read_excel(COMP_CODES_ADDRESS).iloc[:, [1, 2, 3]].drop_duplicates()
issueCodes = pd.read_excel(ISSUE_CODES_ADDRESS).iloc[:, [1, 2, 3]].drop_duplicates()

prodCodes.columns = ['ProdName', 'ProdID', 'ProdGroup']
compCodes.columns = ['ProdGroupCode', 'CompID', 'Component']
issueCodes.columns = ['ProdGroupCode', 'IssueCode', 'Issue']

# Saving the mapping data in dictionaries for later use
prodCodeTrans = {}
prodCodeProdGroupTrans = {}
compCodesTrans = {}
issueCodesTrans = {}
for i in range(prodCodes.shape[0]):
    if pd.isnull(prodCodes.iloc[i, :]['ProdID']):
        continue
    key = str(int(prodCodes.iloc[i, :]['ProdID'])).strip()
    value = str(prodCodes.iloc[i, :]['ProdName']).strip()
    prodCodeTrans[key] = value
for i in range(prodCodes.shape[0]):
    if pd.isnull(prodCodes.iloc[i, :]['ProdID']):
        continue
    key = str(int(prodCodes.iloc[i, :]['ProdID'])).strip()
    value = str(int(prodCodes.iloc[i, :]['ProdGroup'])).strip()
    prodCodeProdGroupTrans[key] = value
for i in range(compCodes.shape[0]):
    if pd.isnull(compCodes.iloc[i, :]['ProdGroupCode']) or pd.isnull(compCodes.iloc[i, :]['CompID']):
        continue
    key1 = compCodes.iloc[i, :]['ProdGroupCode'].strip()
    key2 = compCodes.iloc[i, :]['CompID'].strip()
    value = compCodes.iloc[i, :]['Component'].strip()
    compCodesTrans[key1, key2] = value
for i in range(issueCodes.shape[0]):
    if pd.isnull(issueCodes.iloc[i, :]['ProdGroupCode']) or pd.isnull(issueCodes.iloc[i, :]['IssueCode']):
        continue
    key1 = issueCodes.iloc[i, :]['ProdGroupCode'].strip()
    key2 = issueCodes.iloc[i, :]['IssueCode'].strip()
    value = issueCodes.iloc[i, :]['Issue'].strip()
    issueCodesTrans[key1, key2] = value

# DUE TO INCONSISTENCIES BETWEEN LOG AND DICTIONARY AND CODE TRANSLATION FILES
# ALL CASES ARE RETURNED TO lower CASE
# This data structure is used only for checking the existence of case insensitive P-C-I combinations in the dictionary
def handleText(x):
    # to be used in continue
    if pd.isnull(x):
        return ''
    else:
        return str(x).strip()
dict_pcis = set([handleText(x).lower().strip() + " :: "
                 + handleText(y).lower().strip() + " :: "
                 + handleText(z).strip().lower()
                 for x, y, z in
                 zip(dict_.AffectedProduct,
                     dict_.Component,
                     dict_.CaseIssue)])

# Functions for data post processing in each testID group
def isSCF_OrderTrueFirst(x):
    # checking order by the first appearence
    names_inds = {'SYMPTOM': 1, 'CLASSIFICATIONS': 2, 'FEEDBACK': 3}

    inds_ = []
    namesToNow = set();
    for name in x:
        if name not in namesToNow:
            namesToNow.add(name)
            inds_.append(names_inds[name])

    if len(inds_) == 1:
        return True

    if sum([y < 0 for y in [i - j for i, j in zip(inds_[1:], inds_[:-1])]]) > 0:
        return False
    else:
        return True
def classSuggCodeExtractorTranslator(id, x):
    # extracts the Product-Component-Issues codes from suggestions

    # extracting cases that have product-component-issue
    pcci = re.findall(r'\{\"affectedProduct\":\"(\d*?)\"\,' \
                      r'\"classificationIndex\":(\d?)\,\"component\":\"(.*?)\"\,\"issue\":\"(.*?)\"\}', x)

    # extracting cases that have just product and classificationIndex (Non Technical Issue)
    pc = re.findall(r'\{\"affectedProduct\":\"(\d*?)\"\,\"classificationIndex\":(\d{1})[^,]\}?', x)

    PCIs = set()
    for pci in pcci:
        p = c = i = None

        if pci[0].strip() in prodCodeTrans:
            p = prodCodeTrans[pci[0].strip()]

            if (prodCodeProdGroupTrans[pci[0].strip()], pci[2].strip()) in compCodesTrans:
                c = compCodesTrans[prodCodeProdGroupTrans[pci[0].strip()], pci[2].strip()]
            else:
                componentsNotFound['TestID'].append(id)
                componentsNotFound['ProductGroupCode'].append(prodCodeProdGroupTrans[pci[0].strip()])
                componentsNotFound['ComponentCode'].append(pci[2].strip())

            if (prodCodeProdGroupTrans[pci[0].strip()], pci[3].strip()) in issueCodesTrans:
                i = issueCodesTrans[prodCodeProdGroupTrans[pci[0].strip()], pci[3].strip()]
            else:
                issuesNotFound['TestID'].append(id)
                issuesNotFound['ProductGroupCode'].append(prodCodeProdGroupTrans[pci[0].strip()])
                issuesNotFound['IssueCode'].append(pci[3].strip())

        else:
            prodsNotFound['TestID'].append(id)
            prodsNotFound['AffectedProductCode'].append(pci[0].strip())

        if not p or not c or not i:
            PCIs.add("HAS CODE OR COMBINATION NOT FOUND!")
        else:
            PCIs.add(" :: ".join([p.strip(), c.strip(), i.strip()]))

    for pci in pc:
        if pci[0].strip() in prodCodeTrans:
            p = prodCodeTrans[pci[0].strip()]
            PCIs.add(" :: ".join([p.strip(), '', '']))
        else:
            prodsNotFound['TestID'].append(id)
            prodsNotFound['AffectedProductCode'].append(pci[0].strip())

    return PCIs
def dataEXtraction1(x):

    # Initializing outputs:
    # Calculating duration of event for a testID
    duration = max(x['timeFromFirstAppearance[min]'])

    # Checking S, C, F datatypes existence for a testID and counting them
    requesttype = list(x.requesttype)
    datatypes = ''
    numSCF = [0, 0, 0]

    # Exractable from the symptom log data
    typedQuery = ''
    sympSuggs = ''

    # Extractable from the classification log data
    sympClickPos = 0
    clickedSymp_incClassData = ''
    classSuggs = ''

    # Extractable from the feedback log data
    classClickPos = 0
    finalSymptomSugg = ''
    finalClassSugg = ''
    isFinalClassSetInDict = False
    isFinalClassSetSuggested = False

    # Extracting data from the rows coming from the symptom log data
    if 'SYMPTOM' in requesttype:
        datatypes += 'S'
        numSCF[0] = sum(x.requesttype == 'SYMPTOM')

        typedQueries = x['query'].loc[[a and b for a, b in zip(
            x.requesttype == 'SYMPTOM', x['query'].notnull())]]
        if len(typedQueries) > 0: typedQuery = list(typedQueries)[-1]

        sympSuggs = x['symptom_suggestions'].loc[[a and b and c for a, b, c in zip(
            x.requesttype == 'SYMPTOM', x.symptom_suggestions != '[]', x.symptom_suggestions.notnull())]]
        if len(sympSuggs) == 0: sympSuggs = ['[]']
        sympSuggs = SEP.join(re.findall(r'\"query\":\"(.*?)\"', list(sympSuggs)[-1]))

    # Extracting data from the rows coming from the classification log data
    if 'CLASSIFICATIONS' in requesttype:
        datatypes += 'C'
        numSCF[1] = sum(x.requesttype == 'CLASSIFICATIONS')

        classSuggs = x['classification_suggestions'].loc[[a and b and c for a, b, c in zip(
            x.requesttype == 'CLASSIFICATIONS', x.classification_suggestions != '[]',
            x.classification_suggestions.notnull())]]
        if len(classSuggs) == 0: classSuggs = ['[]']

        sympClickPos = x['selected_symptom'].loc[[a and b for a, b in zip(
            x.requesttype == 'CLASSIFICATIONS', x.selected_symptom.notnull())]]
        if len(sympClickPos) == 0: sympClickPos = -1
        else: sympClickPos = sympClickPos.iloc[-1]

        clickedSymp_incClassData = x['query'].loc[[a and b and c for a, b, c in zip(
            x.requesttype == 'CLASSIFICATIONS', x.classification_suggestions != '[]',
            x.classification_suggestions.notnull())]]
        if len(clickedSymp_incClassData) == 0: clickedSymp_incClassData = ''
        else: clickedSymp_incClassData = clickedSymp_incClassData.iloc[-1]
        classSuggs = SEP.join(classSuggCodeExtractorTranslator(x.testID.iloc[0], list(classSuggs)[-1]))

    # Extracting data from the rows coming from the feedback log data
    if 'FEEDBACK' in requesttype:
        datatypes += 'F'
        numSCF[2] = sum([x == 'FEEDBACK' for x in requesttype])

        classClickPos = x['selected_classification'].loc[[a and b for a, b in zip(
            x.requesttype == 'FEEDBACK', x.selected_classification.notnull())]]
        if len(classClickPos) == 0: sympClickPos = -1
        else: classClickPos = classClickPos.iloc[-1]

        finalSymptomSugg = x['query'].loc[[a and b for a, b in zip(
            x.requesttype == 'FEEDBACK', x['query'].notnull())]]
        if len(finalSymptomSugg) == 0: finalSymptomSugg = ''
        else: finalSymptomSugg = finalSymptomSugg.iloc[-1]

        classSet = x['classificationSet'].loc[[a and b for a, b in zip(
            x.requesttype == 'FEEDBACK', x['classificationSet'].notnull())]]
        if len(classSet) == 0: classSet = '[]'
        else: classSet = classSet.iloc[-1]

        pcci = list(re.findall(r'\{\"affectedProduct\":\"(.*?)\"\,\"component\":\"(.*?)\"\,\"issue\":\"(.*?)\"\}',
                               classSet)[0])
        if 'NON'.lower() in pcci[0].lower() and 'TECHNICAL'.lower() in pcci[0].lower() and \
                        'ISSUE'.lower() in pcci[0].lower():  # Since log's format is different
            pcci[0] = 'NON TECHNICAL ISSUE'
        finalClassSugg = " :: ".join(pcci)

        if finalClassSugg.lower() in dict_pcis:
            isFinalClassSetInDict = True
        if finalClassSugg.lower() in classSuggs.lower():
            isFinalClassSetSuggested = True

    # Saving the number of S, C, F in the data fro this testID
    datatypeCounts = ' - '.join([str(x) for x in numSCF])

    eligProd = None
    eligProdID = list(x.eligibleProductId)[-1]
    if not pd.isnull(eligProdID):
        eligProdID = str(int(float(eligProdID))).strip()
        if eligProdID in prodCodeTrans:
            eligProd = prodCodeTrans[eligProdID]
        else:
            eligProd = 'CodeNotFound'
            eligProdsNotFound['EligibleProductCode'].append(eligProdID)

    else:
        eligProd = 'NoEligProdCited'

    return pd.DataFrame({'testID': list(x['testID'])[-1],
                         'uniqueAgentIDs': [','.join([str(z) for z in set([int(float(y)) for y in x['agentId']
                                                                           if not pd.isnull(y)])
                                                      if not pd.isnull(z)])],
                         'caseID': list(x['caseID'])[-1],
                         'datatypes': [datatypes],
                         'datatypesCount[S-C-F]': [datatypeCounts],
                         'areSCFinOrder': isSCF_OrderTrueFirst(x.requesttype),
                         'typedQuery': [typedQuery],
                         'symptomSuggestions': [sympSuggs],
                         'symptomClickPosition': [sympClickPos],
                         'finalQuery(classificationData)': [clickedSymp_incClassData],
                         'classificationSuggestions': [classSuggs],
                         'classificationClickPosition': [classClickPos],
                         'finalSymptomSuggestion(feedbackData)': [finalSymptomSugg],
                         'finalClassificationSuggestion(feedbackData)': [finalClassSugg],
                         'isFinalClassificationInDictionary': isFinalClassSetInDict,
                         'isFinalClassificationSuggested': isFinalClassSetSuggested,
                         'start_datetime': list(x.start_datetime)[0],
                         'EligibleProduct': eligProd,
                         'duration': [duration],
                         'local': list(x['local'])[-1]})

# Running data aggregation for extracting data from the logs using the defined functions above
g = combinedSCF.groupby('testID', sort=False)  # Using extra memory temporarily for better presentation
logExtracted = progress(g, dataEXtraction1)
COLUMN_ORDER = ['testID', 'uniqueAgentIDs', 'caseID', 'datatypes', 'datatypesCount[S-C-F]', 'areSCFinOrder',
                'typedQuery', 'symptomSuggestions', 'symptomClickPosition', 'finalQuery(classificationData)',
                'classificationSuggestions', 'classificationClickPosition', 'finalSymptomSuggestion(feedbackData)',
                'finalClassificationSuggestion(feedbackData)', 'isFinalClassificationInDictionary',
                'isFinalClassificationSuggested', 'start_datetime', 'EligibleProduct', 'duration', 'local']
logExtracted.reset_index(drop=True, inplace=True)
logExtracted = logExtracted[COLUMN_ORDER]
logExtracted.to_csv(LOG_EXTRACTED_SCF_DEST, index=False)
del g

END = time()
print("\nLog data post-processing (SCF pattern) completed. Time spent: %s minutes.\n" % str(round((END - START) / 60,
                                                                                                  2)))

# ______________________________________________________________________________________________________________________#
# Separating different cases of symptom/classification suggestion/click

# logExtracted_SCF = logExtracted.loc[logExtracted.datatypes == 'SCF', :]  # the following are just for SCF cases
# symClickedClassSuggNotClicked_typedInSuggestions = \
#     logExtracted_SCF.loc[[x and y and z and w for x,y,z,w in
#                           zip(logExtracted_SCF.isAnySymptomClicked == 1,
#                               logExtracted_SCF.hasClassificationSuggestions == 1,
#                               logExtracted_SCF.isAnyClassificationClicked == 0,
#                               logExtracted_SCF.isFinalClassSetSuggested == 1)], :]
# symClickedClassSuggNotClicked_typedNotInSuggestions = \
#     logExtracted_SCF.loc[[x and y and z and w for x,y,z,w in
#                           zip(logExtracted_SCF.isAnySymptomClicked==1,
#                               logExtracted_SCF.hasClassificationSuggestions==1,
#                               logExtracted_SCF.isAnyClassificationClicked==0,
#                               logExtracted_SCF.isFinalClassSetSuggested==0)], :]
# symClickedClassNotSuggNotInDict = logExtracted_SCF.loc[[x and y and z for x,y,z in
#                                                         zip(logExtracted_SCF.isAnySymptomClicked==1,
#                                                             logExtracted_SCF.hasClassificationSuggestions==0,
#                                                             logExtracted_SCF.isFinalClassSetInDict==0)], :]
# symClickedClassNotSuggInDict = logExtracted_SCF.loc[[x and y and z for x,y,z in
#                                                      zip(logExtracted_SCF.isAnySymptomClicked==1,
#                                                          logExtracted_SCF.hasClassificationSuggestions==0,
#                                                          logExtracted_SCF.isFinalClassSetInDict==1)], :]
#
# combinedSCF_symClickedClassSuggNotClicked_typedInSuggestions = \
#     combinedSCF.loc[[x in list(symClickedClassSuggNotClicked_typedInSuggestions.testID)
#                       for x in combinedSCF.testID], :]
# combinedSCF_symClickedClassSuggNotClicked_typedNotInSuggestions = \
#     combinedSCF.loc[[x in list(symClickedClassSuggNotClicked_typedNotInSuggestions.testID)
#                       for x in combinedSCF.testID], :]
# combinedSCF_symClickedClassNotSuggNotInDict = combinedSCF.loc[[x in list(symClickedClassNotSuggNotInDict.testID)
#                                                                for x in combinedSCF.testID], :]
# combinedSCF_symClickedClassNotSuggInDict = combinedSCF.loc[[x in list(symClickedClassNotSuggInDict.testID)
#                                                                for x in combinedSCF.testID], :]
#
# combinedSCF_symClickedClassSuggNotClicked_typedInSuggestions.to_csv(
#     "/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/logData/combinedSCF_symClickedClassSuggNotClicked_"\
#     "typedInSuggestions_logExtracted_%s.csv" % month)
# combinedSCF_symClickedClassSuggNotClicked_typedNotInSuggestions.to_csv(
#     "/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/logData/combinedSCF_symClickedClassSuggNotClicked_"\
#     "typedNotInSuggestions_logExtracted_%s.csv" % month)
# combinedSCF_symClickedClassNotSuggNotInDict.to_csv(
#     "/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/logData/combinedSCF_symClickedClassNotSuggNotInDict_"\
#     "logExtracted_%s.csv" % month)
# combinedSCF_symClickedClassNotSuggInDict.to_csv(
#     "/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/logData/combinedSCF_symClickedClassNotSuggInDict_"\
#     "logExtracted_%s.csv" % month)

print('')

# ______________________________________________________________________________________________________________________#
# Hyun wanted - SC_CF selection approach by Hyun
print('\n', '-' * 100)
print("Starting post-processing the combined log data (SC and CF patterns)... ")
START = time()

def SC_CF_finderTagger(x):

    # Finds SC and CF patterns and makes a new dataframe by the found rows (rows can be repeated for C)
    # the SC and CF patterns will be tagged for
    df_all = pd.DataFrame(None, columns=list(x.columns) + ['SCFTag'])

    # Starting from top if there is any S and C after that save it
    # SC finding algorithm
    sVals = [1 if scf == 'SYMPTOM' else 0 for scf in x.requesttype]
    cVals = [-1 if scf == 'CLASSIFICATIONS' else 0 for scf in x.requesttype]
    fVals = [-5 if scf == 'FEEDBACK' else 0 for scf in x.requesttype]
    vals = [x + y + z for x, y, z in zip(sVals, cVals, fVals)]
    diffVals = [x - y for x, y in zip(vals[0:-1], vals[1:])]
    indSC = [i for i, val in enumerate(diffVals) if val == 2]
    indCF = [i for i, val in enumerate(diffVals) if val == 4]

    for num, ind in enumerate(indSC):
        df_ = x.iloc[ind:ind + 2, :]
        df_['SCFTag'] = 'SC_' + str(num + 1)
        df_all = pd.concat([df_all, df_])

    for num, ind in enumerate(indCF):
        df_ = x.iloc[ind:ind + 2, :]
        df_['SCFTag'] = 'CF_' + str(num + 1)
        df_all = pd.concat([df_all, df_])

    return df_all

print('Finding SC and CF patterns for each testID.')
g1 = combinedSCF.groupby('testID', sort=False)  # Using extra memory temporarily for better presentation
data_ = progress(g1, SC_CF_finderTagger)

print('Processing the data for each testID and its SC and/or CF patterns.')
g2 = data_.groupby(by=['testID', 'SCFTag'], sort=False)  # Using extra memory temporarily for better presentation
logExtracted_SC_CF = progress(g2, dataEXtraction1)
del g1, g2, data_

COLUMN_ORDER = ['testID', 'uniqueAgentIDs', 'caseID', 'datatypes', 'datatypesCount[S-C-F]', 'areSCFinOrder',
                'typedQuery', 'symptomSuggestions', 'symptomClickPosition', 'finalQuery(classificationData)',
                'classificationSuggestions', 'classificationClickPosition', 'finalSymptomSuggestion(feedbackData)',
                'finalClassificationSuggestion(feedbackData)', 'isFinalClassificationInDictionary',
                'isFinalClassificationSuggested', 'start_datetime', 'EligibleProduct', 'duration', 'local']
logExtracted_SC_CF.reset_index(drop=True, inplace=True)
logExtracted_SC_CF = logExtracted_SC_CF[COLUMN_ORDER]
logExtracted_SC_CF.to_csv(LOG_EXTRACTED_SC_CF_DEST, index=False)

END = time()
print("\nLog data post-processing (SC and CF patterns) completed. Time spent: %s minutes.\n" %
      str(round((END - START) / 60, 2)))

# ______________________________________________________________________________________________________________________#
# Saving the final results in a proper format for feeding into the New Symptom Detection pipeline.
print('\n', '-' * 100)
print("Saving the final results in a proper format for feeding into the New Symptom Detection pipeline.")

# Unique PCI names for filtering unauthorized P, C, or I values
prods_ = set([x.lower().strip() for x in prodCodes['ProdName']])
comps_ = set([x.lower().strip() for x in compCodes['Component']])
issues_ = set([x.lower().strip() for x in issueCodes['Issue']])

# SCF patterns
# Selecting candidates from extracted SCF file (using all rows for testID selecting last "qualified" suggestions)
logExtracted_select = logExtracted.loc[['C' in x and 'F' in x for x in logExtracted['datatypes']], :]
pci = [finalClass.strip().split("::") for finalClass in
       logExtracted_select['finalClassificationSuggestion(feedbackData)']]
p = [x[0].strip() for x in pci]
c = [x[1].strip() for x in pci]
i = [x[2].strip() for x in pci]
logData_extr = pd.DataFrame({'Symptoms': logExtracted_select['finalSymptomSuggestion(feedbackData)'],
                             'AffectedProduct': p,
                             'Component': c,
                             'CaseIssue': i,
                             'agentID': logExtracted_select.uniqueAgentIDs,
                             'start_datetime': logExtracted_select.start_datetime
                             })

# Selecting rows with valid PCI (NON TECHNICAL ISSUE will be filtered out in this step if C or I are left empty)
logData_extr = logData_extr.loc[[prod.lower().strip() in prods_ and
                                 comp.lower().strip() in comps_ and
                                 issue.lower().strip() in issues_ for prod, comp, issue in
                                 zip(logData_extr.AffectedProduct, logData_extr.Component, logData_extr.CaseIssue)], :]

logData_extr.to_csv(LOG_EXTRACTED_SCF_DEST_REFORM, index=False)

# SC-CF patterns
# Selecting candidates from extracted SC_CF file (using found SC and CF patterns based on last appearance of S before C
# or C before F)
logExtracted_select = logExtracted_SC_CF[logExtracted_SC_CF['datatypes'] == 'CF']
pci = [finalClass.strip().split("::") for finalClass in
       logExtracted_select['finalClassificationSuggestion(feedbackData)']]
p = [x[0].strip() for x in pci]
c = [x[1].strip() for x in pci]
i = [x[2].strip() for x in pci]
logData_extr = pd.DataFrame({'Symptoms': logExtracted_select['finalSymptomSuggestion(feedbackData)'],
                             'AffectedProduct': p,
                             'Component': c,
                             'CaseIssue': i,
                             'agentID': logExtracted_select.uniqueAgentIDs,
                             'start_datetime': logExtracted_select.start_datetime
                             })

# Selecting rows with valid PCI (NON TECHNICAL ISSUE will be filtered out in this step if C or I are left empty)
logData_extr = logData_extr.loc[[prod.lower().strip() in prods_ and
                                 comp.lower().strip() in comps_ and
                                 issue.lower().strip() in issues_ for prod, comp, issue in
                                 zip(logData_extr.AffectedProduct, logData_extr.Component, logData_extr.CaseIssue)], :]

logData_extr.to_csv(LOG_EXTRACTED_CF_DEST_REFORM, index=False)

# ______________________________________________________________________________________________________________________#
# Saving the unrecognized codes/codes combinations
prodsNotFound = pd.DataFrame(prodsNotFound)
prodsNotFound.drop_duplicates().to_csv(PRODS_NOT_FOUND_DEST, index=False)
componentsNotFound = pd.DataFrame(componentsNotFound)
componentsNotFound.drop_duplicates().to_csv(COMP_NOT_FOUND_DEST, index=False)
issuesNotFound = pd.DataFrame(issuesNotFound)
issuesNotFound.drop_duplicates().to_csv(ISSUE_NOT_FOUND_DEST, index=False)

ALL_END = time()
print('\n', '-' * 100)
print("Process finished. Total time spent: %s minutes.\n" % str(round((ALL_END - ALL_START) / 60, 2)))










