
"""
Created on Aug 1, 2016

@author: eliyarasgarieh
________________________________________________________________________________

This file is written for clustering the expanded symptoms (by keywords) in the dictionary.

The inputs are:
- The address to a .csv file with at least two columns:
    - Symptoms
    - Keywords (comma separated)
- The address to the trained Doc2Vec model used for vectorization.

The output is:
- A .csv file similar to the input with additional columns that identifies the clusters and their size.

"""

import pandas as pd
import numpy as np
import sys, os
import Support_final
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import fcluster
from sklearn.preprocessing import normalize
import pickle
from time import time

# Recording the total run time (printed at the end)
ALL_START = time()

args = sys.argv
DICT_SYMPS_KEYWORDS_ADDRESS = args[1]
TRAINED_MODEL_ADDRESS = args[2]

TAG = ''
SOURCE = '.'
MAX_DIST = 0.3  # Maximum distance for separating teh clusters in hierarchical clusters
LINKAGE = 'average'
if len(args) > 3: TAG = args[3]
if len(args) > 4: SOURCE = args[4]
if len(args) > 5: MAX_DIST = args[5]
if len(args) > 6: LINKAGE = args[6]

VECTORS_DEST = os.path.join(SOURCE, "calculatedFeatureVectors_DictionarySymptoms_method=%s_%s.txt" % (LINKAGE, TAG))
CLUSTERS_DEST = os.path.join(SOURCE, "hierarchicalClusteringDictSymps_method=%s_%s.pkl" % (LINKAGE, TAG))
SYMPS_CLUSTERS_DEST = os.path.join(SOURCE, "clusters_method=%s_minDissim=%s_%s.csv" % (LINKAGE, MAX_DIST, TAG))

# _____________________________________________________________________________________________________________________#
# Loading and preparing the dictionary symptoms and keywords
print('\n', '-' * 100)
print("Loading/preparing the dictionary symptoms by expanding them using the provided keywords ... ")

dictSympsKeywords = pd.read_csv(DICT_SYMPS_KEYWORDS_ADDRESS)
dictSympsKeywords['Keywords'].fillna(' ', inplace=True)
dictSympsKeywords['Symptoms'].fillna(' ', inplace=True)

expandedSymps = [symp + ' '.join([keyword.strip() for keyword in keywrods.split(',')]) for
                 symp, keywrods in zip(dictSympsKeywords['Symptoms'], dictSympsKeywords['Keywords'])]

print("dictionary symptoms expanded/prepared.")

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

# _____________________________________________________________________________________________________________________#
# Finding feature vectors
print('\n', '-'*100)
print("Finding the feature vectors for the expanded symptoms using the trained Doc2Vec model ... ")

supportInstance_.getFeatureVectors(textFileAddress='',
                                   textArray=expandedSymps, tagSeparator=None,
                                   tags=expandedSymps,
                                   contentSeparator=None,
                                   isFileFiltered=False,
                                   isArrayFiltered=False,
                                   isFeatureVectorsAvailable=False,
                                   featureVecsAddress='',
                                   destAddress=VECTORS_DEST)

SEP = ":-:-:"
tags = [''.join(x.split(SEP)[:-1]).strip() for x in open(VECTORS_DEST)]
vecs = [x.split(SEP)[-1].strip() for x in open(VECTORS_DEST)]
vecs = [[float(y) for y in z.split()] for z in vecs]

# Normalizing the vectors to prevent weird errors ("Linkage 'Z' contains negative distances.")
vecs = [normalize(np.array(x)[:, np.newaxis], axis=0).ravel() for x in vecs]

print("Feature vectors calculated and saved.")

# _____________________________________________________________________________________________________________________#
# Clustering using the calculated feature vectors and SciPy packages
print('\n', '-'*100)
print("Starting clustering the symptoms using the feature vectors of the expanded symptoms ... ")

Z = linkage(vecs, method=LINKAGE, metric='cosine')
pickle.dump(Z, open(CLUSTERS_DEST, 'wb'))

# Getting clusters and saving the results
dictSympsKeywords['Clusters'] = fcluster(Z, MAX_DIST, criterion='distance')
dictSympsKeywords.sort_values('Clusters', inplace=True)
clustSize = dictSympsKeywords.groupby('Clusters').apply(lambda x: pd.DataFrame({'ClusterSize': [x.shape[0]]}))
clustSize.reset_index(inplace=True)
dictSympsKeywords = pd.merge(dictSympsKeywords, clustSize, on='Clusters')
dictSympsKeywords = dictSympsKeywords[['Symptoms', 'Keywords', 'Clusters', 'ClusterSize']]
dictSympsKeywords.to_csv(SYMPS_CLUSTERS_DEST, index=False)

print("Clusters found based on the defined maximum distance (= %s)." % MAX_DIST)

#______________________________________________________________________________________________________________________#
ALL_END = time()

print('\n', '-'*100)
print("clustering process finished and the results are saved. Total time spent: %s minutes.\n" %
      str(round((ALL_END - ALL_START)/60, 2)))












