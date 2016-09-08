
'''
Created on July 29, 2016

@author: eliyarasgarieh
________________________________________________________________________________

This file is for expanding a given list of symptoms and weighting them based on their CTR in the given log data.

The inputs are as following:

- The address of a .csv file that contains at least one column of string data (Symptoms).
- The address of a .csv file that is extracted from the log data, and contains at least two columns of string data
  named as "SymptomSuggestions" and "symptomClickPosition". The symptom suggestions should be strings separated with a
  separator that is either assumed as a default value considered below or the one determined as input.
- The address of the trained word2vec model used for expanding the symptoms by adding keywords.
- A symbol used as separator for separating the symptom suggestions (the default is "::-::-::").

The output is:
A .csv file with three columns: 1) Symptoms, 2) added keywords, 3-4) calculated weights for the given symptom
(CTR and CTR - 1 * sd).

'''

import gensim
import pandas as pd
import numpy as np
import sys, os
from Support_final.filters import filter_
from time import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Recording the total run time (printed at the end)
ALL_START = time()

args = sys.argv
SYMPTOM_FILE_ADDRESS = args[1]
LOG_ADDRESS = args[2]
WORD2VEC_MODEL_ADDRESS = args[3]
TAG = ''
if len(args) > 4:
    TAG = args[4]
SEP = " ::-::-::"
if len(args) > 5:
    SEP = args[5]
SOURCE = '.'
if len(args) > 6:
    SOURCE = args[6]

SYMPTOM_COLUMN = 'Symptoms'

DEST_OUTPUT = os.path.join(SOURCE, "expandedWeightedSymptoms_%s.csv" % TAG)

# Functions used for filtering normalizing symptoms (including removing stopwords and lematization)
filterFunc = filter_().filterSentence

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

#_______________________________________________________________________________________________________________________
# Loading the input .csv data file from the provided address
print('\n', '-'*100)
print("Loading/preparing the input symptom files for expansion and weighting based on the log data ... ")

input_ = pd.read_csv(SYMPTOM_FILE_ADDRESS)

# Removing null values (just in case)
input__ = input_[input_[SYMPTOM_COLUMN].notnull()].copy()

# Passing the data from the filtering pipeline and preparing the text document for training the TFIDF model
filteredTexts = [filterFunc(x)[0].split() for x in input__[SYMPTOM_COLUMN]]

# Removing the lines that have filteredText of length zero
input__ = input__[[len(filtText) > 0 for filtText in filteredTexts]]
filteredTexts = [filtText for filtText in filteredTexts if len(filtText) > 0]

print("The data is loaded and prepared.")

#_______________________________________________________________________________________________________________________
# Expanding the symptoms by keywords using TFIDF and Word2Vec models
print('\n', '-'*100)
print("Starting the symptoms expansion by keywords generation, have a cup of coffee or maybe take a nap :) ... ")

def selectTopWords(wordList, n=3):
    # For selecting the top words for expansion based on the TFIDF

    # Removing single numbers at the beginning (don't want them to expand)
    wordList = [word for word in wordList if not word.isdigit()]

    tfidfsTuples = tfidf_model[dict_.doc2bow(wordList)]
    tfidfVals = np.array([x[1] for x in tfidfsTuples])
    ids_ = np.array([x[0] for x in tfidfsTuples])

    # Choosing the top n words based on the TFIDF values
    if len(wordList) > n:
        wordList = [dict_.get(i) for i in ids_[tfidfVals.argsort()[-n:][::-1]]]
        tfidfVals = tfidfVals[tfidfVals.argsort()[-n:][::-1]]

    return list(zip(wordList, tfidfVals))
def expandWord(w, n=5):
    # Finds the keywrods related to w and just chooses the top n unqiue ones after filtering
    TOP_N = n  # finding higher numbers of keywrods since the words can be the same after filtering/cleaning
    keyWordsSelect = set()

    # Checking if the word w is in the model's vocabulary
    if w not in word2vecModel.vocab:
        return ''

    # To make sure that enough keywords are provided
    while len(keyWordsSelect) < n:
        TOP_N *= 2
        keyWords = [filterFunc(x[0])[0] if len(filterFunc(x[0])) > 0 else '' for x in
                    word2vecModel.most_similar(w, topn=TOP_N)]
        for keyWord in keyWords:
            if len(keyWordsSelect) == n:
                break
            if keyWord not in keyWordsSelect:
                if len(keyWord) > 0:
                    keyWordsSelect.add(keyWord)

    return ', '.join(keyWordsSelect)
def expandWords(wordsNum, expansionFactor=2):
    # Expands word list based on the TFIDF scores for each word and the length of the symptom multiplied by the
    # expansion factor.

    expandedWords = []  # Added keywords

    N = wordsNum[0]  # Total numbers of words in the symptom
    wordsTfidf = wordsNum[1]  # Words and their TFIDF scores for finding the numbers of keywords to expand per word
    num_weights = [w[1] for w in wordsTfidf]  # Defining weights for determining numbers of expansions for each word
    num_weights = num_weights/sum(num_weights)
    numWordsToExpand = [int(nw * N * expansionFactor) for nw in num_weights]
    numWordsToExpand[0] += N * expansionFactor - sum(numWordsToExpand)  # making sure sums to N x expansionFactor

    for i in range(len(wordsTfidf)):
        expandedWords += [x.strip() for x in
                          expandWord(wordsTfidf[i][0], n=numWordsToExpand[i]).split(",") if len(x.strip()) > 0]

    return ', '.join(list(set(expandedWords)))
def logger(func):
    # A function for keeping track of calls and progress of using nested function
    def counter(*args, **kwargs):
        progress_ = counter.count * 100/len(filteredTexts)
        sys.stdout.write('\033[D \033[D' * 4 + format(progress_, '3.0f') + '%')
        sys.stdout.flush()
        #print(counter.count)
        counter.count += 1
        return func(*args, **kwargs)

    counter.count = 0
    return counter

# Training the TFIDF model
print("\nTraining TFIDF model for selecting top words for expansion by keyword generation ... ")

dict_ = gensim.corpora.Dictionary(filteredTexts)  # making dictionary object with all vocabulary
corpus_ = [dict_.doc2bow(text) for text in filteredTexts]  # making BOW (corpus)
tfidf_model = gensim.models.TfidfModel(corpus_)  # training TFIDF model

print("TFIDF model is trained.")

# Selecting the words to expand (the output is: (number of words in symptom, [(words, tfidfScores)]))
print("\nSelecting top words in each canonical symptom based on the TFIDF model ...")

wordsToExpand = filteredTexts
wordsToExpand = [(len(words), selectTopWords(words, max(int(len(set(words))/2), 3))) for words in wordsToExpand]

print("Top words are selected for expansion.")

# Loading the gensim word2vec model for expanding the symptoms
print("\nLoading the trained Word2Vec model for keywrod generation ... ")

word2vecModel = gensim.models.word2vec.Word2Vec.load_word2vec_format(WORD2VEC_MODEL_ADDRESS, binary=True)

print("The Word2vec model is loaded.")

# Finding the expanding keywords for the documents
print("\nStarting the keyword generation for the selected words for each symptom (this can take a while)...")
START = time()

sys.stdout.write('Progress:   0%')
sys.stdout.flush()
expandWordWrapper = logger(expandWords)
input__['Keywords'] = [expandWordWrapper(words) for words in wordsToExpand]
sys.stdout.write('\033[D \033[D' * 4 + format(100., '3.0f') + '%' + '\n')
sys.stdout.flush()

END = time()
print("\nThe keywords generation finished. Time spent: %s minutes." % str(round((END - START)/60, 2)))

#_______________________________________________________________________________________________________________________
# Finding the weights for the symptoms using the log data
print('\n', '-'*100)
print("Finding CTRs for the symptoms using the loaded log data ...")

START = time()

# Loading log data and finding symptom suggestions and click positions for calculating CTRs
logData = pd.read_csv(LOG_ADDRESS)

# removing lines with no suggestions (just in case)
logData = logData.loc[logData['symptomSuggestions'].notnull(), :]
sympSuggsClicks = [([sugg.strip() for sugg in suggs.lower().strip().split(SEP)], int(clickPos))
                   for suggs, clickPos in zip(logData['symptomSuggestions'], logData['symptomClickPosition'])]

# Symptoms for measuring their CTR
dataSymp = pd.DataFrame({'Symptoms': input_[SYMPTOM_COLUMN]})
dataSymp.drop_duplicates(inplace=True)

# Calculating CTR values for the Original Symptoms using the log data
def sympIndInSuggs(suggs, symp):
    return np.where(np.array(suggs)==(symp.lower().strip()))[0][0] + 1
def ctrs(data_, suggsClicks=sympSuggsClicks, symptomColName='Symptoms'):
    sympClicks = [[sympsClk[1]==sympIndInSuggs(sympsClk[0], symp) for sympsClk in suggsClicks if
                   symp.lower().strip() in sympsClk[0]] for symp in data_[symptomColName]]
    numSuggs = [len(x) for x in sympClicks]
    numClicks = [sum([y for y in x]) if len(x) > 0 else 0 for x in sympClicks]
    CTRs = [clk/numSugg if numSugg > 0 else 0 for clk, numSugg in zip(numClicks, numSuggs)]
    CTRs_minusSD = [clk/numSugg - np.sqrt(clk/numSugg * (1 - clk/numSugg)/numSugg)
                    if numSugg > 0 else 0 for clk, numSugg in zip(numClicks, numSuggs)]
    CTRs_minusSD = [ctr if ctr > 0 else 0 for ctr in CTRs_minusSD]

    return pd.DataFrame({'CTR': CTRs, 'CTR_minusSD': CTRs_minusSD, 'numSuggs': numSuggs})

# Finding total CTRs
sys.stdout.write('Progress:   0%')
sys.stdout.flush()
g = dataSymp.groupby('Symptoms')
CTRs = progress(g, ctrs, sympSuggsClicks)
sys.stdout.write('\033[D \033[D' * 4 + format(100., '3.0f') + '%' + '\n')
sys.stdout.flush()

CTRs.reset_index(inplace=True)
CTRs = CTRs[['Symptoms', 'CTR', 'CTR_minusSD', 'numSuggs']]

# Replacing the CTRs with the average values for events that has happened less than minimum threshold
MIN_EVENT = 5
AVERAGE_CTR = np.mean(CTRs.CTR)
SD_AVEARAGE_CTR = np.std(CTRs.CTR)/(CTRs.shape[0] ** .5)
INDS_SMALL = CTRs.numSuggs < MIN_EVENT
CTRs.CTR.loc[INDS_SMALL] = AVERAGE_CTR
CTRs.CTR_minusSD.loc[INDS_SMALL] = AVERAGE_CTR - SD_AVEARAGE_CTR
CTRs.CTR_minusSD.loc[CTRs.CTR_minusSD < 0] = 0

END = time()
print("\nCTRs calculated. Time spent: %s minutes." % str(round((END - START)/60, 2)))

#_______________________________________________________________________________________________________________________
# Joining the keywords expansion results with the input including the CTR values
input_ = pd.merge(input_, input__, on=SYMPTOM_COLUMN, how='outer')

#_______________________________________________________________________________________________________________________
# Writing the results as a dataframe to a .csv file
results_ = pd.DataFrame({"Symptoms": input_[SYMPTOM_COLUMN],
              'Keywords': input_['Keywords'],
              'CTR': CTRs.CTR,
              'CTR_minusSD': CTRs.CTR_minusSD})
results_ = results_[[SYMPTOM_COLUMN,
              'Keywords',
              'CTR',
              'CTR_minusSD']]

results_.to_csv(DEST_OUTPUT, index=False)

#______________________________________________________________________________________________________________________#
ALL_END = time()

print('\n', '-'*100)
print("Process finished. Total time spent: %s minutes.\n" % str(round((ALL_END - ALL_START)/60, 2)))








