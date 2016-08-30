

# codes for March 15 meeting
import os, sys, pandas as pd, numpy as np

desired_width = 320    # for better print in console
pd.set_option('display.width', desired_width)

# exec(open('/Users/eliyarasgarieh/PycharmProjects/CG/CG_Functions.py').read()) # loading the written functions if needed; Or:
sys.path.append("/Users/eliyarasgarieh/PycharmProjects/CG/")
from CG_Functions import filter_df

os.chdir('/Users/eliyarasgarieh/Documents/AppleResearch/Data')

# loading data
symClass = pd.read_excel('./CGData/GeneralPurpose/symptomClassification.xlsx', sheetname='Raw_Data')  # classification table
symClass.drop(symClass.columns[[0, 6,8]], axis = 1, inplace=True)
symDic = pd.read_table('./CGData/GeneralPurpose/symptom_dictionary_ranking.tsv')   # CTR and freq table
symMeta = pd.read_table('./CGData/GeneralPurpose/ml_symptoms_meta.txt')  # meta table for connecting Original and Polished names for symptoms
symProdGroups = pd.read_csv('./CGData/GeneralPurpose/uniqueProducts_frequencies.csv') # table provided for separating products under more general groups
symProdGroups.drop(symProdGroups.columns[[0]], axis = 1, inplace=True)

# turning all string columns to lower case and striping leading/trailing white spaces and removing extra characters
filter_df(symClass.ix[:, 4:5])
symClass["AffectedProduct"] = [x.lower().strip() for x in symClass["AffectedProduct"]]
filter_df(symDic)
filter_df(symMeta)
symMeta["Importance_wordlist"] = [', '.join(x.strip().split()) for x in symMeta["Importance_wordlist"]]

# merging tables as a whole
mrg_ = pd.merge(left=symClass, right=symProdGroups, on="AffectedProduct")

symMeta.drop_duplicates("Original_symptom", inplace=True)  # dropping rows with duplicate in the first column
mrg_.rename(columns={"Symptoms":"Original_symptom"}, inplace=True)
mrg_ = pd.merge(left=mrg_, right=symMeta, on="Original_symptom")

temp_ = symDic[["symptom", "freqFromRaw"]].groupby("symptom").sum()  # replacing sum of repeated freqFromRaw after removing duplicates
temp_2 = symDic.groupby("symptom").first()
temp_2["freqFromRaw"] = temp_.ix[:,0] = temp_.ix[:,0]
mrg_ = pd.merge(left=temp_2, right=mrg_, right_on="Polished_symptom", left_index=True)

mrg_ = mrg_.ix[:, [11] + list(range(5, 10)) + [14] + [10] + [13] + list(range(5))] # rearranging columns for better presentation

mrg_.to_csv("./merged_data.csv")


## data analysis

# finding the numbers of unique symptoms and AffectedProducts per product group
symCountPerProdGrp = mrg_[["ProductGroup", "Polished_symptom"]].groupby('ProductGroup').agg(lambda x: len(np.unique(x["Polished_symptom"])))
symCountPerProdGrp.rename(columns={"Polished_symptom":"NumbersOfUniqueSymptoms"}, inplace=True)
symCnt = mrg_[["ProductGroup", "Polished_symptom"]].groupby('ProductGroup').agg('count')
symCountPerProdGrp = pd.merge(left=symCountPerProdGrp, right=symCnt, left_index=True, right_index=True)
symCountPerProdGrp.rename(columns={"Polished_symptom":"TotalNumbersOfSymptoms"}, inplace=True)
symCountPerProdGrp["PercentUnique"] = np.round((symCountPerProdGrp.NumbersOfUniqueSymptoms)/(symCountPerProdGrp.TotalNumbersOfSymptoms)*100)

# studying the distribution of symptoms under each product group
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

documents_ = np.unique(mrg_.Polished_symptom)
stopList = stopwords.words('english')
#stopList = [word.strip().lower() for word in open('./stop_words_mdofied.list')]
texts_ = [[word for word in doc.strip().split() if word not in stopList] for doc in documents_]

from collections import defaultdict # filtering out the tokens that are repeated just one
freqs_ = defaultdict(int)
for text in texts_:
    for token in text:
        freqs_[token]+=1
texts_=[[token for token in text if freqs_[token]>1] for text in texts_]

dict_ = corpora.Dictionary(texts_)
# dict_.save('./CGData/symptoms_dictionary.dict')

# forming BOW corpus
corpus_ = [dict_.doc2bow(text) for text in texts_]
# corpora.BleiCorpus.serialize("/CGData/symtoms_corpus.lda-c", corpus_)

# forming tfidf corpus
tfidf_model = models.TfidfModel(corpus_)
tfidfs_ = [tfidf_model[corp] for corp in corpus_]

# studying similarities
def getIndsForSym(symNames=[''], docs_=['']):  # function for finding the indices of each symptom in the dictionary
    return [docs_.index(x) for x in symNames]

# measuring similarities based of tfidf feature vectors
index_ = similarities.MatrixSimilarity(tfidfs_, num_features=len(dict_.keys()))

# the following can be changed for various productGroup
syms_ = np.unique(mrg_["Polished_symptom"][mrg_.ProductGroup=='3rd-party software'])
inds_ = getIndsForSym(symNames=syms_.tolist(), docs_=documents_.tolist())
featureVecs_ = index_.index[inds_]
sims_ = index_[featureVecs_]
sims_sub = [sim[inds_] for sim in sims_]
# pd.DataFrame(sims_sub).to_csv('./CGData/Processed/sims_tfidf_.csv')
#pd.DataFrame(featureVecs_).to_csv('./CGData/Processed/featureVecs_tfidf_.csv')

# hierarchical clustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster, cophenet
from scipy.spatial.distance import pdist

dends_ = linkage(featureVecs_, 'ward')
max_d=20
dendrogram(
    dends_,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=12,  # show only the last p merged clusters
    show_leaf_counts=False,  # otherwise numbers in brackets are counts
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,  # to get a distribution impression in truncated branches
)
clusters = fcluster(dends_, max_d, criterion='distance')

# finding feature vectors using Word2Vec and Doc2Vec representations
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
labSents_ = [TaggedDocument(words=texts_[i], tags=["sent_%s" % i]) for i in range(len(texts_))]

model_d2v = Doc2Vec(window=4, alpha=0.025, min_alpha=0.025)
model_d2v.build_vocab(labSents_)
for epoch in range(10):
    model_d2v.train(labSents_)
    model_d2v.alpha-=0.002
    model_d2v.min_alpha=model_d2v.alpha

# the following can be changed for various productGroup
syms_ = np.unique(mrg_["Polished_symptom"][mrg_.ProductGroup=='3rd-party software'])
inds_ = getIndsForSym(symNames=syms_.tolist(), docs_=documents_.tolist())
featureVecs_ = [model_d2v.docvecs[i] for i in inds_]
#sims_ = index_[featureVecs_]
#sims_sub = [sim[inds_] for sim in sims_]
#pd.DataFrame(sims_sub).to_csv('./CGData/Processed/sims_d2v_.csv')
pd.DataFrame(featureVecs_).to_csv('./CGData/Processed/featureVecs_d2v_.csv')

# hierarchical clustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

dends_ = linkage(sims_sub, 'ward')
max_d=20
dendrogram(
    dends_,
    truncate_mode='lastp',  # show only the last p merged clusters
    p=12,  # show only the last p merged clusters
    show_leaf_counts=False,  # otherwise numbers in brackets are counts
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,  # to get a distribution impression in truncated branches
)
clusters = fcluster(dends_, max_d, criterion='distance')

# to find the most similar cases to a new query
inferredVec_ = model_d2v.infer_vector([''])
model_d2v.docvecs.most_similar([inferredVec_])

# finding pairwise distances
names = ["3rd-party software", "airport express", "apple pencil","apple remote desktop","apple store", "apple tv", "apple watch", "icloud", "ipad", "iphone","iphoto","ipod",
           "itunes","kenote","os", "macbook pro", "numbers for ios", "pages for ios","photos","siri remote","time capsule"]

from scipy.spatial import distance
dist_pairs = pd.DataFrame(index=names, columns=names)
for i in range(0, len(names)-1):
    temp1_ = pd.read_csv("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv" % ("tfidfs", names[i]))
    temp1_.drop(temp1_.columns[[0]], axis=1, inplace=True)
    for j in range(i + 1,len(names)):
        temp2_ = pd.read_csv("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv" % ("tfidfs", names[j]))
        temp2_.drop(temp2_.columns[[0]], axis=1, inplace=True)
        dists_ = distance.cdist(XA=temp1_.values, XB=temp2_.values)
        dist_pairs.loc[names[i], names[j]] = dist_pairs.loc[names[j], names[i]] = (np.mean(dists_), np.std(dists_))

import pickle
fid = open("betweenGroupSimilarities_euclidean_tfidf.pickle", 'wb')
pickle.dump(dist_pairs, fid)
fid.close()






names = ["3rd-party software", "airport express", "apple pencil","apple remote desktop","apple store", "apple tv", "apple watch", "icloud", "ipad", "iphone","iphoto","ipod",
           "itunes","kenote","os", "macbook pro", "numbers for ios", "pages for ios","photos","siri remote","time capsule"]

from scipy.spatial import distance
dist_pairs = pd.DataFrame(index=names, columns=names)
for i in range(0, len(names)):
    temp1_ = pd.read_csv("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv" % ("tfidfs", names[i]))
    temp1_.drop(temp1_.columns[[0]], axis=1, inplace=True)
    for j in range(i,len(names)):
        temp2_ = pd.read_csv("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv" % ("tfidfs", names[j]))
        temp2_.drop(temp2_.columns[[0]], axis=1, inplace=True)
        dists_ = distance.cdist(XA=temp1_.values, XB=temp2_.values)
        if names[i]==names[j]:
            dataTouse = [dists_[i,j] for i in range(temp1_.shape[0]) for j in range(temp1_.shape[0]) if i > j]
            dist_pairs.loc[names[i], names[j]] = dist_pairs.loc[names[j], names[i]] = (np.mean(dataTouse), np.std(dataTouse))
        else:
            dist_pairs.loc[names[i], names[j]] = dist_pairs.loc[names[j], names[i]] = (np.mean(dists_), np.std(dists_))




