#!usr/bin/env python3

'''
Created on June 22, 2016 (revised several times afterwards)

@author: eliyarasgarieh

This file contains codes for evaluating the effects of dictionary expansion by propagation and adding SETI symptoms.

Inputs:
- Address of the expanded curation dictionary in .xlsx format
- Address of extracted log data (using the log data extraction/processing pipeline) in .csv format. The files with SCF
or SC-CF tags in the outputs from running this pipeline can be used.
- Address of the file containing confirmed/added SETI symptoms in .xlsx format. This file should have one sheet with
 the SETI symptoms in its first column.
- Time interval that data represents (optional, used for tagging)

Outputs:
- Coverage and CTR metrics
- Measured effects of adding SETI symptoms to the dictionary
- Measured effects of propagation symptom-classifications for defined product groups
- Meta data that summarizes the total effects

'''

# Codes for evaluation the effect of dictionary expansion from the log data
import pandas as pd, numpy as np
from collections import defaultdict
import sys, os
from time import time

# Recording the total run time (printed at the end)
START = time()

# Reading the command line arguments and assigning the required values related (constant) variables
args = sys.argv

DICT_ADDRESS = args[1]
EXTRACTED_LOGDATA_ADDRESS = args[2]
SETI_SYMPS_ADDRESS = args[3]
DATE_PERIOD = ''
if len(args) > 4: DATE_PERIOD = args[4]

SOURCE = '.'
DEST_CTR_COVERAGE = os.path.join(SOURCE, "CTRCoverageSymptomClassification_%s.csv" % DATE_PERIOD)
DEST_SYMPTOM_EFFECT = os.path.join(SOURCE, "symptomPropagationEffects_%s.csv" % DATE_PERIOD)
DEST_CLASS_EFFECT = os.path.join(SOURCE, "classPropagationEffects_%s.csv" % DATE_PERIOD)
DEST_EFFECTS_METADATA = os.path.join(SOURCE, "propagationEffects_metaData_%s.csv" % DATE_PERIOD)

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
# Loading the prepared/processed data
logData_extr = pd.read_csv(EXTRACTED_LOGDATA_ADDRESS)

#______________________________________________________________________________________________________________________#
# Loading processing dictionary data
print('\n', '-' * 100)
print("Loading/preparing the symptom-classification dictionary ... ")

def pcisMaker(p, c, i, s):
    if pd.isnull(p): p = ''
    if pd.isnull(c): c = ''
    if pd.isnull(i): i = ''
    if pd.isnull(s): s = ''
    return " ::-::-:: ".join([p.strip(), c.strip(), i.strip(), s.strip()])

dict_ = pd.read_excel(DICT_ADDRESS)
dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']] = \
    dict_.loc[:, ['AffectedProduct', 'Component', 'CaseIssue']].replace(np.nan, '')
dict_.loc[['NON'.lower() in x.lower() and 'TECHNICAL'.lower() in x.lower() and 'ISSUE'.lower() in x.lower()
           for x in dict_.AffectedProduct], 'AffectedProduct'] = 'NON TECHNICAL ISSUE'
dict_['PCIS'] = dict_.groupby(dict_.index).apply(lambda x:
                                                pcisMaker(list(x.AffectedProduct)[0], list(x.Component)[0],
                                                         list(x.CaseIssue)[0], list(x.Symptoms)[0]))

# Saving a dictionary of column names for S-P-C-I values in the "symptom-classification dictionary".
dict_spciColumns = defaultdict(lambda: None)
for s, p, c, i, col in zip(dict_.Symptoms, dict_.AffectedProduct, dict_.Component, dict_.CaseIssue, dict_.Column):
    if pd.isnull(p): p = ''
    if pd.isnull(c): c = ''
    if pd.isnull(i): i = ''
    if pd.isnull(col): col = ''
    s = s.strip().lower()  # Using case insensitive symptoms for keys
    p = p.strip()
    c = c.strip()
    i = i.strip()
    col = col.strip().lower()

    if not dict_spciColumns[(s, p, c, i)]:
        dict_spciColumns[(s, p, c, i)] = set([col])
    else:
        dict_spciColumns[(s, p, c, i)].add(col)

setiSymps = pd.read_excel(SETI_SYMPS_ADDRESS, header=None)
setiSymps = set([x.strip().lower() for x in setiSymps.iloc[:, 0]])
for symp in setiSymps:
    dict_.loc[[x.lower().strip() == symp for x in dict_.Symptoms], 'Column'] = 'seti'

print("Dictionary loaded and prepared.")

#______________________________________________________________________________________________________________________#
# Using cases with testIDs for evaluation
print('\n', '-' * 100)
print("Loading and preparing the extracted log file ...")

# Measuring cases that have symptom suggestions and what percent are clicked (Symptom coverage/CTR)
logData_extr_SC = logData_extr.loc[['SC' in x for x in logData_extr.datatypes], :]
logData_extr_SC = logData_extr_SC[[pd.notnull(a) and len(a) > 0 for a in logData_extr_SC.typedQuery]]
logData_extr_S = logData_extr.loc[['S' in x for x in logData_extr.datatypes], :]  # Just for coverage (for comparison)
logData_extr_S = logData_extr_S[[pd.notnull(a) and len(a) > 0 for a in logData_extr_S.typedQuery]]

# Studying the classification suggestions and clicks for clicked symptoms (classification coverage/CTR)
logData_extr_CF = logData_extr.loc[['CF' in x for x in logData_extr.datatypes], :]
logData_extr_C = logData_extr.loc[['C' in x for x in logData_extr.datatypes], :]  # Just for coverage (for comparison)

print("The extracted log file loaded and prepared.")

#______________________________________________________________________________________________________________________#
# Metric calculations

# Symptom coverage/CTR
numSC = logData_extr_SC.shape[0]
numSympSugg = sum(logData_extr_SC.symptomSuggestions.notnull())
numClicksInSympSugg = sum([x and y for x, y in zip(logData_extr_SC.symptomSuggestions.notnull(),
                                          logData_extr_SC.symptomClickPosition > 0)])
symptomCoverage = numSympSugg/numSC
symptomCTR = numClicksInSympSugg/numSympSugg
symptomCTR_overall = symptomCoverage * symptomCTR

# Just for comparing its effect on symptom coverage measurements
numS = logData_extr_S.shape[0]
numSympSugg_S = sum(logData_extr_S.symptomSuggestions.notnull())
symptomCoverage_S = numSympSugg_S/numS

# Classification coverage/CTR
numCF = logData_extr_CF.shape[0]
numClassSugg = sum(logData_extr_CF.classificationSuggestions.notnull())
numClicksInClassSugg = sum([x and y for x, y in zip(logData_extr_CF.classificationSuggestions.notnull(),
                                          logData_extr_CF.classificationClickPosition > 0)])
classCoverage = numClassSugg/numCF
classCTR = numClicksInClassSugg/numClassSugg
classCTR_overall = classCoverage * classCTR

# Just for comparing its effect on classification coverage measurements
numC = logData_extr_C.shape[0]
numClassSugg_C = sum(logData_extr_C.classificationSuggestions.notnull())
classCoverage_C = numClassSugg_C/numC

ctrCoverages = pd.DataFrame({'numSC': [numSC],
                             'numS': [numS],
                             'numCF': [numCF],
                             'numC': [numC],
                             'numSympSugg(SC)': [numSympSugg],
                             'numSympSugg(S)': [numSympSugg_S],
                             'numClicksInSympSugg': [numClicksInSympSugg],
                             'symptomCoverage(SC)': [symptomCoverage],
                             'symptomCoverage(S)': [symptomCoverage_S],
                             'symptomCTR': [symptomCTR],
                             'symptomCTR_overall': [symptomCTR_overall],
                             'classCoverage(CF)': [classCoverage],
                             'classCoverage(C)': [classCoverage_C],
                             'classCTR': [classCTR],
                             'classCTR_overall': [classCTR_overall],
                             'TotalNumUniqueAgents': len(set(logData_extr.uniqueAgentIDs))})

ctrCoverages.to_csv(DEST_CTR_COVERAGE)

#______________________________________________________________________________________________________________________#
# Investigating the expansion effect by looking at the classification suggestions and SETI reports
print('\n', '-' * 100)
print("Starting metric calculations ... ")

def percSeti(x, setiSymps):
    # This function is written to the effect of expanding the dictionary by the SETI report expansion using the rows of
    # extracted-log data (to be used by the SC or SCF data)

    # Initializing outputs:
    setiSymps = setiSymps
    testID = list(x['testID'])[0]
    numSympSuggs = 0
    numSuggsInSeti = 0
    isFinalSympInSeti = False
    isAnySympClicked = list(x['symptomClickPosition'])[0]
    isFinalSympInSuggs = False

    # Processing
    if pd.isnull(list(x['symptomSuggestions'])[0]): x['symptomSuggestions'] = ''
    suggs = [symp.lower().strip() for symp in list(x['symptomSuggestions'])[0].split("::-::-::")]

    if pd.isnull(list(x['finalQuery(classificationData)'])[0]): x['finalQuery(classificationData)'] = ['']
    finalSymp = list(x['finalQuery(classificationData)'])[0].lower().strip()

    numSympSuggs = len([sugg for sugg in suggs if len(sugg) > 0])
    numSuggsInSeti = sum([x in setiSymps for x in suggs])
    isFinalSympInSeti = finalSymp in setiSymps
    isFinalSympInSuggs = finalSymp in suggs

    return pd.DataFrame({'testID': testID,
                         'numSymptomsSuggested': [numSympSuggs],
                         'numSuggsInSeti': [numSuggsInSeti],
                         'isFinalSympInSeti': [isFinalSympInSeti],
                         'isAnySympClicked': [isAnySympClicked],
                         'isFinalSympInSuggs': [isFinalSympInSuggs]})
def percProp(x, dict_spciColumns, setiSymps):
    # This function is written to the effect of expanding the dictionary by propagation report expansion using the rows
    # of extracted-log data (to be used by the CF or SCF data).

    # Initializing outputs:
    testID = list(x['testID'])[0]
    setiSymps = setiSymps
    numClassSuggs = 0
    numSuggsInProp = 0
    isFinalClassInProp = False
    isAnyClassClicked = list(x['classificationClickPosition'])[0]
    isFinalClassInSuggs = False
    isFinalSympInSeti = False

    # Processing
    if pd.isnull(list(x['classificationSuggestions'])[0]): x['classificationSuggestions'] = ''
    suggs = [class_.strip().split("::") for class_ in list(x['classificationSuggestions'])[0].split("::-::-::")
             if len(class_) > 0]
    suggs = [(p.strip(), c.strip(), i.strip()) for p, c, i in suggs]

    if pd.isnull(list(x['finalClassificationSuggestion(feedbackData)'])[0]):
        x['finalClassificationSuggestion(feedbackData)'] = [' :: :: ']
    finalP, finalC, finalI = list(x['finalClassificationSuggestion(feedbackData)'])[0].strip().split("::")
    finalP, finalC, finalI = finalP.strip(), finalC.strip(), finalI.strip()

    if pd.isnull(list(x['finalSymptomSuggestion(feedbackData)'])[0]): x['finalSymptomSuggestion(feedbackData)'] = ''
    finalSymp = list(x['finalSymptomSuggestion(feedbackData)'])[0].lower().strip()

    numClassSuggs = len([sugg for sugg in suggs if len(sugg) > 0])
    numSuggsInProp = sum(['propagated' in dict_spciColumns[finalSymp, sugg[0].strip(), sugg[1].strip(),
                                                           sugg[2].strip()] if
                          not pd.isnull(dict_spciColumns[finalSymp, sugg[0].strip(), sugg[1].strip(),
                                                           sugg[2].strip()]) else False
                          for sugg in suggs if len(sugg) == 3])
    isFinalClassInProp = 'propagated' in dict_spciColumns[finalSymp, finalP, finalC, finalI] if not \
        pd.isnull(dict_spciColumns[finalSymp, finalP, finalC, finalI]) else False
    isFinalClassInSuggs = (finalP, finalC, finalI) in suggs
    isFinalSympInSeti = finalSymp in setiSymps

    return pd.DataFrame({'testID': [testID],
                         'numClassSuggs': [numClassSuggs],
                         'numSuggsInProp': [numSuggsInProp],
                         'isFinalClassInProp': [isFinalClassInProp],
                         'isAnyClassClicked': [isAnyClassClicked],
                         'isFinalClassInSuggs': [isFinalClassInSuggs],
                         'isFinalSympInSeti': [isFinalSympInSeti]})

print("\nMeasuring the effect of expanding the symptom-classification dictionary by the SETI symptoms ...")
g = logData_extr_SC.groupby(logData_extr_SC.index)
symptomEffects = progress(g, percSeti, setiSymps)

print("\nMeasuring the effect of expanding the symptom-classification dictionary by the propagation ...")
g = logData_extr_CF.groupby(logData_extr_CF.index)
classEffects = progress(g, percProp, dict_spciColumns, setiSymps)

symptomEffects.to_csv(DEST_SYMPTOM_EFFECT)
classEffects.to_csv(DEST_CLASS_EFFECT)

print("Done with the metric calculation.")

#______________________________________________________________________________________________________________________#
# Calculating meta data for summarizing the evaluations

symptProp = pd.read_csv(DEST_SYMPTOM_EFFECT)
classProp = pd.read_csv(DEST_CLASS_EFFECT)
print('numSymp = ' ,symptProp.shape[0])
print('numClass = ' ,classProp.shape[0])
print('numSympSugg = ', sum(symptProp.numSymptomsSuggested>0))
print('numClassSugg = ', sum(classProp.numClassSuggs>0))
print('numSympClicked = ', sum(symptProp.isAnySympClicked>0))
print('numClassClicked = ', sum(classProp.isAnyClassClicked>0))
print('Numbers of Classification suggestion with at least one Propagated case = ', sum(classProp.numSuggsInProp>0))
print('Numbers of Final Classification Coming from Propagations', sum(classProp.isFinalClassInProp==True))
print('Numbers of Final Classification Coming from Propagations (clicked)',
      sum([x and y for x,y in zip(classProp.isFinalClassInProp==True, classProp.isAnyClassClicked>0)]))
print('Number of Symptoms Suggestions with at Least one fromSETI',
      sum(symptProp.numSuggsInSeti>0))
print('Numbers of Final Symptom Coming from SETI', sum(symptProp.isFinalSympInSeti>0))
print('Numbers of Final Symptom Coming from SETI (clicked)',
      sum([x and y for x,y in zip(symptProp.isFinalSympInSeti>0, symptProp.isAnySympClicked>0)]))

pd.DataFrame({'Numbers of Symptoms Records': [symptProp.shape[0]],
              'Numbers of Classifications Records': [classProp.shape[0]],
              'Numbers of Symptom Suggestions': [sum(symptProp.numSymptomsSuggested>0)],
              'Numbers of Classification Suggestions': [sum(classProp.numClassSuggs>0)],
              'Numbers of Symptoms Suggestions Clicked': [sum(symptProp.isAnySympClicked > 0)],
              'Numbers of Classification Suggestions Clicked': [sum(classProp.isAnyClassClicked > 0)],
              'Numbers of Classification suggestion with at least one Propagated case = ':
                  [sum(classProp.numSuggsInProp>0)],
              'Numbers of Final Classification Coming from Propagations': [sum(classProp.isFinalClassInProp==True)],
              'Numbers of Final Classification Coming from Propagations (clicked)':
                  [sum([x and y for x, y in zip(classProp.isFinalClassInProp == True,
                                                classProp.isAnyClassClicked > 0)])],
              'Number of Symptoms Suggestions with at Least one fromSETI': [sum(symptProp.numSuggsInSeti > 0)],
              'Numbers of Final Symptom Coming from SETI': [sum(symptProp.isFinalSympInSeti>0)],
              'Numbers of Final Symptom Coming from SETI (clicked)':
                  [sum([x and y for x, y in zip(symptProp.isFinalSympInSeti > 0, symptProp.isAnySympClicked > 0)])]
              }).to_csv(DEST_EFFECTS_METADATA)

END = time()
print('\n', '-' * 100)
print("Process finished. Total time spent: %s minutes.\n" % str(round((END - START) / 60, 2)))



