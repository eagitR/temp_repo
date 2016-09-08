
'''
Created on Aug 12, 2016

@author: eliyarasgarieh

This file contains codes for generating the nGram flat file for the given symptoms.

The input:
- A .csv file containing a symptom column (called "symptom" by default)
- Extracted file from log (using symptoms and classification tables) with at least two columns:
    - Typed query: typed symptom in symptom table (named 'typedQuery' by default)
    - Symptom: the symptom in the dictionary that represent typed symptom (clicked symptom in classification table,
    called "symptom" by default).
- Extracted log file with at least two columns called "symptomSuggestions" and "symptomClickPosition" for scoring the
symptoms based on win, loss, tie situations.

The output:
- A .csv file with n-grams (n = 1-5) with the following schema: 'typeahead', 'symptom', 'method_type', "Win", "Loss",
"Tie", "AverageWinPosition", 'weight'
    - 'typeahead': infix n-gram
    - 'symptom': the symptom used for finding infix n-gram
    - 'method_type': a tag for the applied n-gram
    - 'Win': numbers of wins based on log
    - 'Loss': Numbers of loss based on log
    - 'Tie': Numbers of ties based on log
    - 'weight': weights defined using the defined link function (see the function inside code)

This is a flat file, and each n-gram is repeated for all applicable symptoms.

** The "symptoms" column in dictionary and other files all called "symptom/

'''

import pandas as pd
import numpy as np
from nltk import ngrams
import re
import os
import sys
from time import time

# Recording the total run time (printed at the end)
ALL_START = time()

args = sys.argv

SYMP_FILE_ADDRESS = args[1]
TYPED_SYMPTOM_FILE_ADDRESS = args[2]
LOG_ADDRESS = args[3]

SYMP_COLUMN_NAME = 'symptom'
TYPED_COLUMN_NAME = 'typedQuery'

SOURCE = "."
SEP = " ::-::-::"
NUM_NGRAMS = 10

DEST_TYPE_AHEAD_WEIGHTED = os.path.join(SOURCE, "logNgrams_tokensLetters_winLossTieWeighted.csv")

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
# Finding ngrams for the symptoms
print('\n', '-' * 100)
print("Finding ngrams for (dictionary) symptoms and typed queries in clicked data (in the log) ... ")

def simpleFilter(s):
    return re.sub("[^a-zA-Z0-9\s\+\-]+",'', s)
def infixLetterNgrams(sent, dn = 3, minLength = 3):

    if len(sent) < minLength:
        return []

    ngram_ = set()
    for i in range(minLength, len(sent) + 1, dn):
        ng_ = sent[:i].strip()
        ngram_.add(ng_)

    return list(ngram_)

sympsTable = pd.read_csv(SYMP_FILE_ADDRESS)
typedSympsTable = pd.read_csv(TYPED_SYMPTOM_FILE_ADDRESS)

# Definign length of ngrams based on length of symptoms
NUM_NGRAMS = max([len(x.strip().split()) for x in set(sympsTable[SYMP_COLUMN_NAME])])
nGrams = {}

# Finding token ngrams for the dictionary symptoms
for n in range(1, NUM_NGRAMS + 1):
    nGramName = 'word_ngram_%d' % n
    nGrams[nGramName] = {}
    for symp in set(sympsTable[SYMP_COLUMN_NAME]):
        symp_clean = simpleFilter(symp)
        ngrams_ = set([' '.join(list(ng)) for ng in ngrams(symp_clean.strip().lower().split(), n)])
        for ng in ngrams_:
            if ng in nGrams[nGramName]:
                nGrams[nGramName][ng].add(symp)
            else:
                nGrams[nGramName][ng] = set()
                nGrams[nGramName][ng].add(symp)

            # Adding letter ngrams
            ngs_ = infixLetterNgrams(ng, dn=1, minLength=3)
            for ng_ in ngs_:
                if ng_ in nGrams[nGramName]:
                    nGrams[nGramName][ng_].add(symp)
                else:
                    nGrams[nGramName][ng_] = set()
                    nGrams[nGramName][ng_].add(symp)

# Finding token ngrams for typed symptoms from the log (clicked data with final symptom in the dictionary)
for n in range(1, NUM_NGRAMS + 1):
    nGramName = 'word(typed)_ngram_%d' % n
    nGrams[nGramName] = {}
    for i, symp in enumerate(typedSympsTable[TYPED_COLUMN_NAME]):
        symp_clean = simpleFilter(symp)
        ngrams_ = set([' '.join(list(ng)) for ng in ngrams(symp_clean.strip().lower().split(), n)])
        for ng in ngrams_:
            if ng in nGrams[nGramName]:
                nGrams[nGramName][ng].add(typedSympsTable.iloc[i, :][SYMP_COLUMN_NAME])
            else:
                nGrams[nGramName][ng] = set()
                nGrams[nGramName][ng].add(typedSympsTable.iloc[i, :][SYMP_COLUMN_NAME])

            # Adding letter ngrams
            ngs_ = infixLetterNgrams(ng, dn=1, minLength=3)
            for ng_ in ngs_:
                if ng_ in nGrams[nGramName]:
                    nGrams[nGramName][ng_].add(typedSympsTable.iloc[i, :][SYMP_COLUMN_NAME])
                else:
                    nGrams[nGramName][ng] = set()
                    nGrams[nGramName][ng].add(typedSympsTable.iloc[i, :][SYMP_COLUMN_NAME])

# Preparing flat data file
data_ = {'typeahead':[], 'method_tag':[], SYMP_COLUMN_NAME: []}
for n in range(1, NUM_NGRAMS + 1):
    nGramName = 'word_ngram_%d' % n
    for ng in nGrams[nGramName]:
        for symp in nGrams[nGramName][ng]:
            data_['method_tag'] += [nGramName]
            data_['typeahead'] += [ng]
            data_[SYMP_COLUMN_NAME] += [symp]

for n in range(1, NUM_NGRAMS + 1):
    nGramName = 'word(typed)_ngram_%d' % n
    for ng in nGrams[nGramName]:
        for symp in nGrams[nGramName][ng]:
            data_['method_tag'] += [nGramName]
            data_['typeahead'] += [ng]
            data_[SYMP_COLUMN_NAME] += [symp]

data_ = pd.DataFrame(data_)

#______________________________________________________________________________________________________________________#
# Finding the numbers of wins, losses, ties, and win by position, and scoring based on these values
print('\n', '-' * 100)
print("Calculating scores for symptoms based on win, loss, tie situations... ")

def linkFunction(x):
    return np.exp(x)/(1 + np.exp(x))

# Loading the log data
logData = pd.read_csv(LOG_ADDRESS)
logData = logData.loc[logData['symptomSuggestions'].notnull(), :]

# Loading the symptom file
dataSymp = pd.DataFrame({'symptom': sympsTable[SYMP_COLUMN_NAME]})
dataSymp.drop_duplicates(inplace=True)

# Extracting the suggestions and click positions from the data
sympSuggsClicks = [([sugg.strip() for sugg in suggs.lower().strip().split(SEP)], int(clickPos))
                   for suggs, clickPos in zip(logData['symptomSuggestions'], logData['symptomClickPosition'])]

# functions for finding the metrics for scoring
def sympIndInSuggs(suggs, symp):
    return np.where(np.array(suggs) == (symp.lower().strip()))[0][0] + 1
def winLossMetrics(data_,suggsClicks=sympSuggsClicks, symptomColName='symptom'):
    # This function should be used by grouping based on symptoms
    symp = data_[symptomColName].iloc[0]

    pos_ = [(sympIndInSuggs(sympsClk[0], symp), sympsClk[1]) for sympsClk in suggsClicks if
            (symp.lower().strip() in sympsClk[0])]

    winPos_ = [x[0] for x in pos_ if x[0] == x[1]]
    wins_ = len(winPos_)
    winPosAve_ = 0
    if wins_ > 0:
        winPosAve_ = sum(winPos_) / wins_

    loss_ = sum([x[0] < x[1] or x[1] == 0 for x in pos_])
    tie_ = sum([x[0] > x[1] and x[1] > 0 for x in pos_])

    return pd.DataFrame({'Win': [wins_],
                         'Loss': [loss_],
                         'Tie': [tie_],
                         'AverageWinPosition': [winPosAve_]})

# Finding metrics for symptoms
sys.stdout.write('Progress:   0%')
sys.stdout.flush()
g = dataSymp.groupby(SYMP_COLUMN_NAME)
metrics_ = progress(g, winLossMetrics, sympSuggsClicks)
sys.stdout.write('\033[D \033[D' * 4 + format(100., '3.0f') + '%' + '\n')
sys.stdout.flush()

metrics_.reset_index(inplace=True)
metrics_['weight'] = [linkFunction(x - z/y) if y != 0 else linkFunction(-z) for x, y, z in
                      zip(metrics_['AverageWinPosition'], metrics_['Win'], metrics_['Loss'])]

data_ = pd.merge(data_, metrics_, on=SYMP_COLUMN_NAME)
data_ = data_[['typeahead', SYMP_COLUMN_NAME, 'weight', 'method_tag', 'Win', 'Loss', 'AverageWinPosition']]

data_.to_csv(DEST_TYPE_AHEAD_WEIGHTED, index=False)

#______________________________________________________________________________________________________________________#
ALL_END = time()

print('\n', '-'*100)
print("Preparing type ahead table and ranking finished. Total time spent: %s minutes.\n" %
      str(round((ALL_END - ALL_START)/60, 2)))






