'''
Created on Aug 12, 2016

@author: eliyarasgarieh

Short script for assessing ngram model's performance

The input:
- The output of nGramModel.py

The output:
- The log data (from log data extraction pipeline) for assessing coverage of the n-gram model.

'''


import pandas as pd
import re
import sys

args = sys.argv

NGRAM_DATA_ADDRESS = args[1]
LOG_DATA_SC_CF_ADDRESS = args[2]

def simpleFilter(s):
    return re.sub("[^a-zA-Z0-9\s\+\-]+",'', s)

#______________________________________________________________________________________________________________________#
# Loading the ngram data
ngramData = pd.read_csv(NGRAM_DATA_ADDRESS)
ngs_ = set([x.lower().strip() for x in ngramData.typeahead if pd.notnull(x)])

#______________________________________________________________________________________________________________________#
# Loading the log data
logData_extr = pd.read_csv(LOG_DATA_SC_CF_ADDRESS)
logData_extr_sc = logData_extr.loc[['SC' in x for x in logData_extr.datatypes], :]
logData_extr_sc = logData_extr_sc.loc[logData_extr_sc.typedQuery.notnull(), :]
logData_extr_sc_clk = logData_extr_sc.loc[logData_extr_sc.symptomClickPosition > 0, :]
logData_extr_sc_clk = logData_extr_sc_clk.loc[logData_extr_sc_clk.symptomSuggestions.notnull(), ]

#______________________________________________________________________________________________________________________#
# Assessing based on exact string match
totalCases = logData_extr_sc.shape[0]
totalSuggCases = sum(logData_extr_sc.symptomSuggestions.notnull())
numsInForTotal = sum([simpleFilter(s).strip().lower() in ngs_ for s in logData_extr_sc.typedQuery])
numsInForNoSuggs = sum([simpleFilter(s).strip().lower() in ngs_ for
     s in logData_extr_sc.typedQuery.loc[logData_extr_sc.symptomSuggestions.isnull()]])

coverageForTotal = numsInForTotal/totalCases
coverageForNoSuggs = numsInForNoSuggs / (totalCases - totalSuggCases)

print('\n', '-' * 100)
print("The coverage of n-grams (type ahead) model for in the given log (all log) is: %s", coverageForTotal)

print('\n', '-' * 100)
print("The coverage of n-grams (type ahead) model for in the given log (with no suggestion) is: %s", coverageForTotal)

# Trustworthy clicked data for CTR evaluation
logData_extr_sc_clk_t = logData_extr_sc_clk.loc[logData_extr_sc_clk['finalQuery(classificationData)'].notnull(), ]
logData_extr_sc_clk_t = logData_extr_sc_clk_t.loc[[x.lower().strip() in y.lower() for x, y in
                                                             zip(logData_extr_sc_clk_t[
                                                                     'finalQuery(classificationData)'],
                                                                 logData_extr_sc_clk_t.symptomSuggestions)], :]

# Choosing the ones with valid sympotm suggestions (there are cases that symptom suggestion is not in the dictionary)
allDictSymps = set([x.strip() for x in ngramData.symptom])
logData_extr_sc_clk_t = logData_extr_sc_clk_t.loc[[symp.strip() in allDictSymps for symp in
                                                   logData_extr_sc_clk_t['finalQuery(classificationData)']], :]

numsInForClk = sum([simpleFilter(s).strip().lower() in ngs_ for s in logData_extr_sc_clk_t.typedQuery])
coverageForClk = numsInForClk / logData_extr_sc_clk_t.shape[0]

print('\n', '-' * 100)
print("The coverage of n-grams (type ahead) model for in the given log (using clicked data) is: %s", coverageForClk)














