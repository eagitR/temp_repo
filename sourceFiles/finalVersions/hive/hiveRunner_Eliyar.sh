

# For getting daat from hive and saving it in local directory
echo 'Getting data from' $1 'to ' $2 ' (from symptom, classification, feedback tables in the aml_cg database)';

# Creating temporary folder with small overlap possibility with other folders
hdfs dfs -mkdir tempCGData_1726354527182735_$1_$2;
hdfs dfs -mkdir tempCGData_1726354527182735_$1_$2/symptoms
hdfs dfs -mkdir tempCGData_1726354527182735_$1_$2/classifications
hdfs dfs -mkdir tempCGData_1726354527182735_$1_$2/feedback

OUTDIR_SYMP=tempCGData_1726354527182735_$1_$2/symptoms
OUTDIR_CLASS=tempCGData_1726354527182735_$1_$2/classification
OUTDIR_FEED=tempCGData_1726354527182735_$1_$2/feedback

hive --hiveconf var1=$1 --hiveconf var2=$2 --hiveconf var3=$OUTDIR_SYMP --hiveconf var4=$OUTDIR_CLASS -hiveconf var5=$OUTDIR_FEED -f hiveCodes_Eliyar.hql

# Merging the data saved on he HDFS
MERGE_ADDRESS_SYMP=./symptoms_$1_$2
MERGE_ADDRESS_CLASS=./classifications_$1_$2
MERGE_ADDRESS_FEED=./feedback_$1_$2

hdfs dfs -getmerge $OUTDIR_SYMP $MERGE_ADDRESS_SYMP
hdfs dfs -getmerge $OUTDIR_CLASS $MERGE_ADDRESS_CLASS
hdfs dfs -getmerge $OUTDIR_FEED $MERGE_ADDRESS_FEED

hdfs dfs -rm -r tempCGData_1726354527182735_$1_$2;

# Alternative solution when tab separation causes problem
cat $MERGE_ADDRESS_SYMP | sed -r 's/[\x01]/::-::-::/g' > "$MERGE_ADDRESS_SYMP.txt"
cat $MERGE_ADDRESS_CLASS | sed -r 's/[\x01]/::-::-::/g' > "$MERGE_ADDRESS_CLASS.txt"
cat $MERGE_ADDRESS_FEED | sed -r 's/[\x01]/::-::-::/g' > "$MERGE_ADDRESS_FEED.txt"

rm $MERGE_ADDRESS_SYMP
rm $MERGE_ADDRESS_CLASS
rm $MERGE_ADDRESS_FEED

