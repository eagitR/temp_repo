

# script for handling CG data
setwd('/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/')
library(openxlsx)
library(data.table)  # the fread command automatically handles the missing values and various separators
library(plyr)
library(dplyr)

tolower_ <- function(data) {
  data[] = sapply(data, tolower)
  return(data)
}

symClass <- read.xlsx('./symptomClassification.xlsx', sheet = 'Raw_Data', startRow = 1, colNames = TRUE)
symClass$Markdown <- NULL
symClass$Column <- NULL
symClass$X9 <- NULL

symDic <- read.table('./symptom_dictionary_ranking.tsv', header = TRUE, sep = '\t')
symMeta <- fread('./ml_symptoms_meta.txt', data.table = FALSE)
symProductGroups <- read.csv('./uniqueProducts_frequencies.csv')
symProductGroups$X <- NULL
aggrByGroup <- ddply(.data = symProductGroups, .variables = 'ProductGroup', function(x) data.frame(FreqsOfProdGroup=sum(x$FreqOfAffectedProduct)))
symProductGroups <- merge(symProductGroups, aggrByGroup, by = 'ProductGroup')

# turning all symptom names to lowercase
symClass <- tolower_(symClass)
symDic <- tolower_(symDic)
symMeta <- tolower_(symMeta)[, c(1,4,3)]

# resolving dulicates problem in symMeta and symDic by deleting or aggregating (num elligible products in symDic)
symMeta <- symMeta[!duplicated(symMeta$Original_symptom), ]
symDic$freqFromRaw <- as.numeric(symDic$freqFromRaw)
symDicAgg <- ddply(.data = symDic, .variables = 'symptom', .fun = function(x) data.frame(x[1,1:5], freqFromRow=sum(x[, 6])))
symDicAgg <- arrange(symDicAgg, desc(freqFromRow))

# #*** I stopped here since there are Symptoms in symClass that are not in original symptoms in the symMeta and I will not consider using the other table at this point
# # joinng tables: symdicUnique -> symMeta -> symClass on symptoms
# symConnect <- merge(x = symMeta, y = symClass, by.x = "Orginal_symptom", by.y = "Symptoms")
# 
# # getting rid of rows with non utf-8 characters
# symAl$Original_symptom <- iconv(symAl$Original_symptom, "UTF-8", "UTF-8", "123456789")
# indToRemove <- grep("123456789", symAl$Original_symptom)
# symAl <- symAl[-indToRemove, ]
# 
# symAll <- merge(x = symAl, y = symClass, by.x = "Original_symptom", by.y = "Symptoms")

# simplifying the table for later use
# quartz(); hist(symAll$numImpression, breaks = 100, xlab = "numImpression", ylab = "", main = "Histogram of Numbers of Impression")
# quartz(); hist(symAll$numClicked, breaks = 100, xlab = "numClicked", ylab = "", main = "Histogram of Numbers of Clicked")
# quartz(); hist(symAll$CTR, breaks = 100, xlab = "CTR", ylab = "", main = "Histogram of CTR")
# quartz(); hist(symAll$CTR_LB, breaks = 100, xlab = "CTR_LB", ylab = "", main = "Histogram of CTR_LB (symptom importance)")
# quartz(); plot(x = symAll$CTR, y = symAll$CTR_LB, xlab = "CTR", ylab = "CTR_LB")

# joing symClass and symProductGroup tables for grouping on the product groups
symClassProdGroups <- merge(y = symClass, x = symProductGroups, by="AffectedProduct")
symClassProdGroups <- symClassProdGroups[, c(2, 5, 1, 6:8, 3, 4)]

# finding the BOW matrix/vectors using the selected weighting approach
library(tm)
# using the 

source <- VectorSource(symClas)


# ****************visualizing/postprocessing data analysis results from Python
prepForPlotPydata <- function(data){
  data$X <- NULL
  return(data)
}

cos_sim <- read.csv('./processed/sims_tfidf_3rd-party software.csv')
featureVecs_ <- read.csv('./processed/featureVecs_tfidfs_3rd-party software.csv')

cos_sim <- as.matrix(prepForPlotPydata(cos_sim))
featureVecs_ <- prepForPlotPydata(featureVecs_)
quartz(); corrplot(cos_sim)
quartz(); corrplot(cor(t(featureVecs_)))

# finding correlation matrices
highProds <- c("apple tv", "apple watch", "icloud",  "ipad", "iphone", "ipod", "itunes", "non technical issue")
for (prod in highProds){
  temp <- read.csv(sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv","tfidfs", prod))
  cor_ <- cor(t(prepForPlotPydata(temp)))
  write.csv(x = cor_, file = sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/covariance_%s_%s.csv", "tfidfs", prod))
  temp <- read.csv(sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv","d2v", prod))
  cor_ <- cor(t(prepForPlotPydata(temp)))
  write.csv(x = cor_, file = sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/covariance_%s_%s.csv", "d2v", prod))
}

# finding pairwise similarity statistics between groups
 
#   library(pdist)   # very inefficent, crashes
# names_ <- c("3rd-party software", "airport express", "apple pencil","apple remote desktop","apple store", "apple tv", "apple watch", "icloud", "ipad", "iphone","iphoto","ipod",
#            "itunes","kenote","os", "macbook pro", "numbers for ios", "pages for ios","photos","siri remote","time capsule")
# 
# dist_pairs <- list()
# for (i in 1:(length(names_) - 1)){
#   temp1_ <- prepForPlotPydata(read.csv(sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv","tfidfs", names_[i])))
#   for (j in (i+1):length(names_)){
#     temp2_ <- prepForPlotPydata(read.csv(sprintf("/Users/eliyarasgarieh/Documents/AppleResearch/Data/CGData/processed/featureVecs_%s_%s.csv","tfidfs", names_[j])))
#     dists_ <- as.matrix(pdist(X = temp1_, Y = temp2_))
#     dist_pairs[[paste(names_[i], names_[j], sep = " , ")]] <- c(mean=mean(dists_), std=sd(dists_)) 
#   }
#   cat("finished: ", i, " , ", j)
# }

# loading Python calculations
bSim_tfidf <- read.csv('./Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_euclidean.csv', stringsAsFactors = FALSE)
bSim_d2v <- read.csv('./Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_euclidean.csv', stringsAsFactors = FALSE)
rownames(bSim_tfidf) <- bSim_tfidf[[1]]; bSim_tfidf$X <- NULL
rownames(bSim_d2v) <- bSim_d2v[[1]]; bSim_d2v$X <- NULL
colnames(bSim_tfidf) <- rownames(bSim_tfidf)
colnames(bSim_d2v) <- rownames(bSim_d2v)

parsFromPython <- function(x) {
  nums = trimws(strsplit(x, ",")[[1]])
  mean_ = as.numeric(substr(nums[1], 2, nchar(nums[1])))
  std_ = as.numeric(substr(nums[2], 1, nchar(nums[2])-1))
  return(c(mean_, std_))
}

bSim_tfidf_mean <- bSim_tfidf; bSim_tfidf_std <- bSim_tfidf
bSim_d2v_mean <- bSim_d2v; bSim_d2v_std <- bSim_d2v
for (i in 1:dim(bSim_tfidf_mean)[1]){
  for (j in 1:dim(bSim_tfidf_mean)[2]){
    nums_ <- parsFromPython(bSim_tfidf[i,j])
    bSim_tfidf_mean[i,j] <- nums_[1]
    bSim_tfidf_std[i,j] <- nums_[2]
    nums_ <- parsFromPython(bSim_d2v[i,j])
    bSim_d2v_mean[i,j] <- nums_[1]
    bSim_d2v_std[i,j] <- nums_[2]
  }
}

write.csv(bSim_tfidf_mean, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_means_euclidean.csv')
write.csv(bSim_tfidf_std, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_stds_euclidean.csv')
write.csv(bSim_d2v_mean, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_means_euclidean.csv')
write.csv(bSim_d2v_std, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_stds_euclidean.csv')


bSim_tfidf <- read.csv('./Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_correlation.csv', stringsAsFactors = FALSE)
bSim_d2v <- read.csv('./Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_correlation.csv', stringsAsFactors = FALSE)
rownames(bSim_tfidf) <- bSim_tfidf[[1]]; bSim_tfidf$X <- NULL
rownames(bSim_d2v) <- bSim_d2v[[1]]; bSim_d2v$X <- NULL
colnames(bSim_tfidf) <- rownames(bSim_tfidf)
colnames(bSim_d2v) <- rownames(bSim_d2v)

bSim_tfidf_mean <- bSim_tfidf; bSim_tfidf_std <- bSim_tfidf
bSim_d2v_mean <- bSim_d2v; bSim_d2v_std <- bSim_d2v
for (i in 1:dim(bSim_tfidf_mean)[1]){
  for (j in 1:dim(bSim_tfidf_mean)[2]){
    nums_ <- parsFromPython(bSim_tfidf[i,j])
    bSim_tfidf_mean[i,j] <- nums_[1]
    bSim_tfidf_std[i,j] <- nums_[2]
    nums_ <- parsFromPython(bSim_d2v[i,j])
    bSim_d2v_mean[i,j] <- nums_[1]
    bSim_d2v_std[i,j] <- nums_[2]
  }
}

write.csv(bSim_tfidf_mean, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_means_correlation.csv')
write.csv(bSim_tfidf_std, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_tfidfs_stds_correlation.csv')
write.csv(bSim_d2v_mean, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_means_correlation.csv')
write.csv(bSim_d2v_std, file = './Documents/AppleResearch/Data/CGData/processed/betweenGroupSimilarities_d2v_stds_correlation.csv')



mrg_ <- read.csv('./Documents/AppleResearch/Data/CGData/merged_data.csv')
x <- table(mrg_$Polished_symptom)
x <- as.data.frame(x)
x <- x[order(x$Freq, decreasing = TRUE), ]
colnames(x) <- c("Polished_Symptoms", "Frequency")

selectData <- x[1:100, ]
selectData$`Highest Repeated Products` <- NA
for (i in 1:100){
  data_ <- subset(mrg_, mrg_$Polished_symptom==selectData$Polished_Symptoms[i])
  prods_ <-as.data.frame(table(data_$ProductGroup))
  prods_ <- prods_[order(prods_$Freq, decreasing = TRUE), ]
  sortSelect <- NULL
  for (j  in 1:min(5, dim(prods_)[1])){
    temp <- paste0(prods_[j,1], " (", prods_[j,2], ")")
    sortSelect <- paste(sortSelect, temp, sep=", ")
  }
  selectData$`Highest Repeated Products`[i] <- substr(sortSelect, 2, nchar(sortSelect))
}
write.csv(selectData, file = "./Documents/AppleResearch/Data/CGData/allSymptomsFrequency_ProdFreq.csv")

#############