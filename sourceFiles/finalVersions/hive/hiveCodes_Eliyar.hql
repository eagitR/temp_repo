
-- Pulling data from symptom, classification, feedback tables between thedetermined dates
-- The time frame will be from starting of start date (00:00:00) to the end of end date (23:59:59)

set hive.cli.print.header=true;
set hive.exec.compress.output=false;
set mapreduce.job.queuename=Applications_other;
set hive.exec.plan=;
use aml_cg;

INSERT OVERWRITE DIRECTORY '${hiveconf:var3}'
SELECT source, requesttype, trim(request_data), trim(get_json_object(request_data,'$.testId')) as testID, requestid, traceid, start_timestamp, end_timestamp, from_unixtime(cast(start_timestamp/1000 as BigInt)) as start_datetime, from_unixtime(cast(end_timestamp/1000 as BigInt)) as end_datetime, trim(get_json_object(request_data, '$.timestamp')) as timestamp_inRequestData, trim(query), trim(get_json_object(request_data, '$.productGroupFamilyId')) as productGroupFamilyId, trim(get_json_object(request_data, '$.productGroupId')) as productGroupId, trim(get_json_object(request_data, '$.affectedProductId')) as affectedProductId, trim(get_json_object(request_data, '$.eligibleProductId')) as eligibleProductId, trim(get_json_object(request_data, '$.agentId')) as agentId, trim(get_json_object(response_data, '$.suggestions')) as symptom_suggestions, month, year
FROM cgsymptoms WHERE source='iLog_v1.5.0' AND from_unixtime(cast(start_timestamp/1000 as BigInt))>from_unixtime(unix_timestamp('${hiveconf:var1} 00:00:00', 'yyyy-MM-dd HH:mm:ss')) AND from_unixtime(cast(start_timestamp/1000 as BigInt))<from_unixtime(unix_timestamp('${hiveconf:var2} 23:59:59', 'yyyy-MM-dd HH:mm:ss')) AND length(get_json_object(request_data,'$.testId'))>0;

INSERT OVERWRITE DIRECTORY '${hiveconf:var4}'
SELECT source, requesttype, request_data, get_json_object(request_data,'$.testId') as testID, start_timestamp, end_timestamp, from_unixtime(cast(start_timestamp/1000 as BigInt)) as start_datetime, from_unixtime(cast(end_timestamp/1000 as BigInt)) as end_datetime, get_json_object(request_data, '$.timestamp') as timestamp_inRequestData, query, get_json_object(request_data, '$.productGroupFamilyId') as productGroupFamilyId, get_json_object(request_data, '$.productGroupId') as productGroupId, get_json_object(request_data, '$.affectedProductId') as affectedProductId, get_json_object(request_data, '$.eligibleProductId') as eligibleProductId, get_json_object(request_data, '$.agentId') as agentId, get_json_object(request_data, '$.symptomIndex') as selected_symptom, get_json_object(response_data, '$.CLASSIFICATIONS') as classification_suggestions
FROM cgclassification WHERE source='iLog_v1.5.0' AND from_unixtime(cast(start_timestamp/1000 as BigInt))>from_unixtime(unix_timestamp('${hiveconf:var1} 00:00:00', 'yyyy-MM-dd HH:mm:ss')) AND from_unixtime(cast(start_timestamp/1000 as BigInt))<from_unixtime(unix_timestamp('${hiveconf:var2} 23:59:59', 'yyyy-MM-dd HH:mm:ss')) AND length(get_json_object(request_data,'$.testId'))>0;

INSERT OVERWRITE DIRECTORY '${hiveconf:var5}'
SELECT source, requesttype, request_data, get_json_object(request_data,'$.testId') as testID, start_timestamp, end_timestamp, from_unixtime(cast(start_timestamp/1000 as BigInt)) as start_datetime, from_unixtime(cast(end_timestamp/1000 as BigInt)) as end_datetime, get_json_object(request_data, '$.timestamp') as timestamp_inRequestData, query, get_json_object(request_data, '$.productGroupFamilyId') as productGroupFamilyId, get_json_object(request_data, '$.productGroupId') as productGroupId, get_json_object(request_data, '$.affectedProductId') as affectedProductId, get_json_object(request_data, '$.eligibleProductId') as eligibleProductId, get_json_object(request_data, '$.agentId') as agentId, get_json_object(request_data, '$.caseId') as caseID, get_json_object(request_data, '$.classificationSet') as classificationSet, get_json_object(request_data, '$.classificationIndex') as selected_classification
FROM cgfeedback WHERE source='iLog_v1.5.0' AND from_unixtime(cast(start_timestamp/1000 as BigInt))>from_unixtime(unix_timestamp('${hiveconf:var1} 00:00:00', 'yyyy-MM-dd HH:mm:ss')) AND from_unixtime(cast(start_timestamp/1000 as BigInt))<from_unixtime(unix_timestamp('${hiveconf:var2} 23:59:59', 'yyyy-MM-dd HH:mm:ss')) AND length(get_json_object(request_data,'$.testId'))>0;









