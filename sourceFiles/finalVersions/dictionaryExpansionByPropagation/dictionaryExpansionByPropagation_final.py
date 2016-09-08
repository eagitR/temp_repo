#!usr/bin/env python3

'''
Created on May30, 2016

@author: eliyarasgarieh

This file contains codes for expanding symptom-classification (curation) dictionary, by propagating the symptom, and
product-component-issues between product groups.

Inputs:
- Address of curation dictionary (in .xlsx format)
- Address of directory that contains Product, Component, Issue mapping files with the following names (if the names change minor corrections are required):
    - productToGroupMap_v4.0.xlsx
    - componentMap_v4.0.xlsx
    - issueMap_v4.0.xlsx

Outputs:
- The expanded dictionary
- The expanded components mapping file
- The expanded case issue mapping file

'''

# codes for expanding dictionary

import pandas as pd
import os, sys
from time import time

START = time()

# Reading the command line arguments and assigning the required values related (constant) variables
args = sys.argv

DICT_ADDRESS = args[1]
MAP_CODE_DIR = args[2]

PROD_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "productToGroupMap_v4.0.xlsx")
COMP_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "componentMap_v4.0.xlsx")
ISSUE_CODES_ADDRESS = os.path.join(MAP_CODE_DIR, "issueMap_v4.0.xlsx")

SOURCE = '.'
EXPANDED_DICT_ADDRESS = os.path.join(SOURCE, "symptomClassification_v4.2_expanded_Grouping")
EXPANDED_COMPS_ADDRESS = os.path.join(SOURCE, "newComponentMapping_Grouping")
EXPANDED_ISSUES_ADDRESS = os.path.join(SOURCE, "newIssueMapping_Grouping")

# ______________________________________________________________________________________________________________________#
# Reading the cleaned dictionary
print('\n', '-' * 100)
print("Loading preparing curation dictionary ...")

dict_ = pd.read_excel(DICT_ADDRESS)
dict_.drop_duplicates(list(dict_.columns), inplace=True)

# Loading the component and issue tables for checking the existence of component and issue for the product
print('\n', '-' * 100)
print("Loading the mapping files and preparing translation dictionaries ...")

prodCodes = pd.read_excel(PROD_CODES_ADDRESS)
compCodes = pd.read_excel(COMP_CODES_ADDRESS)
issueCodes = pd.read_excel(ISSUE_CODES_ADDRESS)

prodCodes.drop_duplicates(list(prodCodes.columns), inplace=True)
compCodes.drop_duplicates(list(compCodes.columns), inplace=True)
issueCodes.drop_duplicates(list(issueCodes.columns), inplace=True)

compCodes['Column'] = ' '
issueCodes['Column'] = ' '

caseReturnComponents = {}
for comp in set(compCodes.Component):
    caseReturnComponents[comp.lower().strip()] = comp

caseReturnIssues = {}
for issue in set(issueCodes.Issue):
    caseReturnIssues[issue.lower().strip()] = issue
    
    
grpProdMap = {} 
for i in range(prodCodes.shape[0]):
    prodGrp = str(prodCodes.iloc[i, 3]).strip()
    prodName = str(prodCodes.iloc[i, 0]).lower().strip()
    grpProdMap[prodName] = prodGrp
        
prodGrpMap = {}
for i in range(prodCodes.shape[0]):
    prodGrp = str(prodCodes.iloc[i, 3]).strip()
    prodName = str(prodCodes.iloc[i, 0]).lower().strip()
    if prodGrp in prodGrpMap:
        prodGrpMap[prodGrp].add(prodName)
    else:
        prodGrpMap[prodGrp]=set()
        prodGrpMap[prodGrp].add(prodName)

compProdGrps = {}
for i in range(compCodes.shape[0]):
    prodGrp = str(compCodes.iloc[i, 1]).strip()
    compName = str(compCodes.iloc[i, 3]).lower().strip()
    if compName in compProdGrps:
        compProdGrps[compName].add(prodGrp)
    else:
        compProdGrps[compName]=set()
        compProdGrps[compName].add(prodGrp)

issueProdGrps = {}
for i in range(issueCodes.shape[0]):
    prodGrp = str(issueCodes.iloc[i, 1]).strip()
    issueName = str(issueCodes.iloc[i, 3]).lower().strip()
    if issueName in issueProdGrps:
        issueProdGrps[issueName].add(prodGrp)
    else:
        issueProdGrps[issueName]=set()
        issueProdGrps[issueName].add(prodGrp)
        
compProdCodeMap = {} 
for i in range(compCodes.shape[0]):
    comp = str(compCodes.iloc[i, 3]).lower().strip()
    compGrp = str(compCodes.iloc[i, 2]).strip()
    prodGrp = str(compCodes.iloc[i, 1]).strip()
    compProdCodeMap[comp, prodGrp] = compGrp

issueProdCodeMap = {} 
for i in range(issueCodes.shape[0]):
    issue = str(issueCodes.iloc[i, 3]).lower().strip()
    issueGrp = str(issueCodes.iloc[i, 2]).strip()
    prodGrp = str(issueCodes.iloc[i, 1]).strip()
    issueProdCodeMap[issue, prodGrp] = issueGrp

compCodeProdCodeMap = {} 
for i in range(compCodes.shape[0]):
    comp = str(compCodes.iloc[i, 3]).lower().strip()
    compGrp = str(compCodes.iloc[i, 2]).strip()
    prodGrp = str(compCodes.iloc[i, 1]).strip()
    prodName = str(compCodes.iloc[i, 0]).lower().strip()
    compCodeProdCodeMap[comp, compGrp, prodGrp] = prodName
    
issueCodeProdCodeMap = {} 
for i in range(issueCodes.shape[0]):
    issue = str(issueCodes.iloc[i, 3]).lower().strip()
    issueGrp = str(issueCodes.iloc[i, 2]).strip()
    prodGrp = str(issueCodes.iloc[i, 1]).strip()
    prodName = str(issueCodes.iloc[i, 0]).lower().strip()
    issueCodeProdCodeMap[issue, issueGrp, prodGrp] = prodName

# The following products groups are used for grouping the affected/eligible products by string matching
# Defining product groups:
prodGroups_0 = { # coarse groups
    'apple pencil': ['apple pencil'],
    
    'apple watch': ['apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm',
                    'apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 38mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch hermes 42mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm'],
    
    'ipad': ['ipad',
             'ipad (3rd gen) wi-fi',
             'ipad (3rd gen) wi-fi + cellular',
             'ipad (3rd gen) wi-fi + cellular (vz)',
             'ipad (3rd generation) wi-fi',
             'ipad (3rd generation) wi-fi + cellular',
             'ipad (3rd generation) wi-fi + cellular (vz)',
             'ipad (4th gen) wi-fi',
             'ipad (4th gen) wi-fi + cellular',
             'ipad (4th gen) wi-fi + cellular (mm)',
             'ipad 2',
             'ipad 2 3g',
             'ipad 2 3g (verizon)',
             'ipad 2 3g verizon',
             'ipad 2 wi-fi',
             'ipad 3g',
             'ipad air 2 wi-fi',
             'ipad air 2 wifi, cellular',
             'ipad air wi-fi',
             'ipad air wi-fi, cellular',
             'ipad mini (retina) wi-fi',
             'ipad mini (retina) wi-fi, cellular',
             'ipad mini 2 wi-fi',
             'ipad mini 2 wi-fi, cellular',
             'ipad mini 3 wi-fi',
             'ipad mini 3 wi-fi, cellular',
             'ipad mini 4 wi-fi',
             'ipad mini 4 wi-fi, cellular',
             'ipad mini wi-fi',
             'ipad mini wi-fi + cellular',
             'ipad mini wi-fi + cellular (mm)',
             'ipad mini wi-fi, cellular',
             'ipad mini wi-fi, cellular (mm)',
             'ipad pro 12.9-inch wi-fi',
             'ipad pro 12.9-inch wi-fi, cellular',
             'ipad pro 9.7-inch wi-fi',
             'ipad pro 9.7-inch wi-fi, cellular',
             'ipad pro wi-fi',
             'ipad pro wi-fi, cellular'],

    'iphone': ['iphone',
               'iphone 3gs (8gb)',
               'iphone 4',
               'iphone 4 (8gb)',
               'iphone 4 cdma',
               'iphone 4 cdma (8gb)',
               'iphone 4s',
               'iphone 4s (8gb)',
               'iphone 5',
               'iphone 5c',
               'iphone 5s',
               'iphone 6',
               'iphone 6 plus',
               'iphone 6s',
               'iphone 6s plus'],
        
    'ipod': ['ipod nano (7th generation)',
             'ipod touch (4th generation late 2011)',
             'ipod touch (4th generation)',
             'ipod touch (5th generation)'],
        
    'macbook': ['macbook pro (13-inch, mid 2012)',
                'macbook pro (retina, 13-inch,early 2015)']
        }  
prodGroups_1 = {  # Detailed on iphone and ipad groups
    'apple pencil': ['apple pencil'],
    
    'apple watch': ['apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm',
                    'apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 38mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch hermes 42mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm'],
    
    'ipad2-4': ['ipad',
             'ipad 2',
             'ipad 2 3g',
             'ipad 2 3g (verizon)',
             'ipad 2 3g verizon',
             'ipad 3g'
             ],
        
    'ipad2-4Wifi': [
             'ipad mini wi-fi',
             'ipad 2 wi-fi',
             'ipad air 2 wi-fi',
             'ipad mini 2 wi-fi',
             'ipad mini 3 wi-fi',
             'ipad mini 4 wi-fi',
             'ipad (3rd gen) wi-fi',
             'ipad (3rd generation) wi-fi',
             'ipad (4th gen) wi-fi',
             'ipad air wi-fi',
             'ipad mini (retina) wi-fi'
             ],
             
    'ipad2-4Cellular': [
            'ipad air 2 wifi, cellular',
            'ipad air wi-fi, cellular',
            'ipad (3rd generation) wi-fi + cellular',
            'ipad (3rd generation) wi-fi + cellular (vz)',
            'ipad (3rd gen) wi-fi + cellular',
            'ipad (3rd gen) wi-fi + cellular (vz)',
             'ipad (4th gen) wi-fi + cellular',
             'ipad (4th gen) wi-fi + cellular (mm)',             
             'ipad mini (retina) wi-fi, cellular',
             'ipad mini 2 wi-fi, cellular',
             'ipad mini 3 wi-fi, cellular',
             'ipad mini 4 wi-fi, cellular',
             'ipad mini wi-fi + cellular',
             'ipad mini wi-fi + cellular (mm)',
             'ipad mini wi-fi, cellular',
             'ipad mini wi-fi, cellular (mm)'
             ],
    
    'ipadProWifi': [
             'ipad pro 12.9-inch wi-fi',
             'ipad pro wi-fi',
             'ipad pro 9.7-inch wi-fi'
             ],
        
    'ipadProCellular': [
             'ipad pro 12.9-inch wi-fi, cellular',
             'ipad pro 9.7-inch wi-fi, cellular',
             'ipad pro wi-fi, cellular'                 
             ],

    'iphone3-4': ['iphone',
               'iphone 3gs (8gb)',
               'iphone 4',
               'iphone 4 (8gb)',
               'iphone 4 cdma',
               'iphone 4 cdma (8gb)',
               'iphone 4s',
               'iphone 4s (8gb)'
               ],
        
    'iphone5-6': ['iphone 5',
               'iphone 5c',
               'iphone 5s',
               'iphone 6',
               'iphone 6 plus',
               'iphone 6s',
               'iphone 6s plus'
               ],
        
    'ipod': ['ipod nano (7th generation)',
             'ipod touch (4th generation late 2011)',
             'ipod touch (4th generation)',
             'ipod touch (5th generation)'
             ],
        
    'macbook': ['macbook pro (13-inch, mid 2012)',
                'macbook pro (retina, 13-inch,early 2015)'
                ]
         } 
prodGroups_2 = {  # Detailed on iphone and ipad groups (just for newer products)
    'apple pencil': ['apple pencil'],
    
    'apple watch': ['apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm',
                    'apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 38mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch hermes 42mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm'],
        
    'ipad4MiniAirWifi': [
             'ipad mini wi-fi',
             'ipad air 2 wi-fi',
             'ipad mini 2 wi-fi',
             'ipad mini 3 wi-fi',
             'ipad mini 4 wi-fi',
             'ipad air wi-fi',
             'ipad mini (retina) wi-fi'
             ],
             
    'ipad4MiniCellular': [
             'ipad mini (retina) wi-fi, cellular',
             'ipad mini 2 wi-fi, cellular',
             'ipad mini 3 wi-fi, cellular',
             'ipad mini 4 wi-fi, cellular',
             'ipad mini wi-fi + cellular',
             'ipad mini wi-fi + cellular (mm)',
             'ipad mini wi-fi, cellular',
             'ipad mini wi-fi, cellular (mm)'
             ],
    
    'ipadProWifi': [
             'ipad pro 12.9-inch wi-fi',
             'ipad pro wi-fi',
             'ipad pro 9.7-inch wi-fi'
             ],
        
    'ipadProCellular': [
             'ipad pro 12.9-inch wi-fi, cellular',
             'ipad pro 9.7-inch wi-fi, cellular',
             'ipad pro wi-fi, cellular'                 
             ],
        
    'iphone5-6': ['iphone 5',
               'iphone 5c',
               'iphone 5s',
               'iphone 6',
               'iphone 6 plus',
               'iphone 6s',
               'iphone 6s plus'
               ],
        
    'ipod': ['ipod nano (7th generation)',
             'ipod touch (4th generation late 2011)',
             'ipod touch (4th generation)',
             'ipod touch (5th generation)'
             ],
        
    'macbook': ['macbook pro (13-inch, mid 2012)',
                'macbook pro (retina, 13-inch,early 2015)'
                ]
         }
prodGroups_3 = {  # Detailed on iphone and ipad groups (just for newest products)
    'apple pencil': ['apple pencil'],
    
    'apple watch': ['apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm',
                    'apple watch 38mm',
                    'apple watch 42mm',
                    'apple watch edition 38mm',
                    'apple watch edition 42mm',
                    'apple watch hermes 38mm',
                    'apple watch hermes 42mm',
                    'apple watch sport 38mm',
                    'apple watch sport 42mm'],
                         
    'ipadProWifi': [
             'ipad pro 12.9-inch wi-fi',
             'ipad pro wi-fi',
             'ipad pro 9.7-inch wi-fi'
             ],
        
    'ipadProCellular': [
             'ipad pro 12.9-inch wi-fi, cellular',
             'ipad pro 9.7-inch wi-fi, cellular',
             'ipad pro wi-fi, cellular'                 
             ],
        
    'iphone5-6': ['iphone 5',
               'iphone 5c',
               'iphone 5s',
               'iphone 6',
               'iphone 6 plus',
               'iphone 6s',
               'iphone 6s plus'
               ],
        
    'ipod': ['ipod nano (7th generation)',
             'ipod touch (4th generation late 2011)',
             'ipod touch (4th generation)',
             'ipod touch (5th generation)'
             ],
        
    'macbook': ['macbook pro (13-inch, mid 2012)',
                'macbook pro (retina, 13-inch,early 2015)'
                ]
         }

prodGroups_ = prodGroups_2

print('\n', '-' * 100)
print("Expanding the dictionary based on the defined product groups ...")

def anyIn(x):
    return sum([x.lower() in prodGroups_[prod] for prod in prodGroups_]) > 0

# Finding rows with equal AffectedProduct and EligibleProduct if they are in the above product groups
rows_toExpand = [str(x).lower().strip()==str(y).lower().strip() and anyIn(x) for x,y in zip(dict_.AffectedProduct,
                                                                                            dict_.EligibleProduct)]
dict_toExpand = dict_.loc[rows_toExpand, :]

# Finding all Component (C) - CaseIssue (I) - Symptom (S) combinations for each of the product groups
# and collecting them in a set (uniques)
CIS = {}
for prod in prodGroups_:
    rows_ = [x.lower().strip() in prodGroups_[prod] for x in dict_toExpand.AffectedProduct]
    cis_ = [str(x).strip().lower() + " ::-:: " + str(y).strip().lower() + " ::-:: " + str(z).strip() for x,y,z in
            zip(dict_toExpand.loc[rows_, 'Component'], dict_toExpand.loc[rows_, 'CaseIssue'], dict_toExpand.loc[rows_, 'Symptoms'])
            if not pd.isnull(x) and not pd.isnull(y) and not pd.isnull(z)]
    CIS[prod] = set(cis_)

# Looking at the C-I combinations of each affected product in the selected rows of the dictionary (dict_toExpand)
# and adding the non-existent C-Is in the related product group
# For C-I that are propagated the term "PROPAGATED" is inserted in the "Column" column of the dictionary.
def whichGroup(x):
    for prod in prodGroups_:
        if x.lower().strip() in prodGroups_[prod]:
            return prod

# Expanding the dictionary and Componenet - Issue files
allProds = set(dict_toExpand.AffectedProduct)
newPCIS = {'AffectedProduct':[], 'EligibleProduct':[], 'Component':[], 'CaseIssue':[], 'Symptoms':[], 'Column':[]}
newPCcode = {'Product_Line (GCRM_PARENT_PROD_DESC)':[], 'Group_Code (PROD_GROUP_CD)':[], 'comp_id':[], 'Component':[]}
newPIcode = {'Product_Line':[], 'Group_Code':[], 'Issue_Cd':[], 'Issue':[]}

for affProd in allProds:
    # Finding "C :: I :: S" combinations for the AffectedProduct
    prodCis_ = set([x.strip() for x in [str(x).strip().lower() + " ::-:: " + str(y).strip().lower() + " ::-:: " +
                                        str(z).strip().lower() for x,y,z in
            zip(dict_toExpand.loc[dict_toExpand.AffectedProduct==affProd, 'Component'],
                dict_toExpand.loc[dict_toExpand.AffectedProduct==affProd, 'CaseIssue'],
                dict_toExpand.loc[dict_toExpand.AffectedProduct==affProd, 'Symptoms'])]])
    
    # Getting all the related CIS for the affected products group 
    cis_= CIS[whichGroup(affProd)]
    
    # Adding the CIS that are in the group but not under this affected product to the affected product
    for cis in cis_:
        str_ = cis.lower()
        if str_ not in prodCis_:
            c, i, s = cis.split("::-::")
            pname = affProd.lower().strip()
            
            if pname not in grpProdMap:
                continue
            
            if c.strip() not in compProdGrps or i.strip() not in issueProdGrps:
                continue

            prodCode = str(grpProdMap[pname]).strip()
            
            if prodCode not in compProdGrps[c.strip()] or prodCode not in issueProdGrps[i.strip()]:
                continue
            
            prods = prodGrpMap[prodCode]
            compCode = compProdCodeMap[c.strip(), prodCode]
            issueCode = issueProdCodeMap[i.strip(), prodCode]
            
            # adding the nonexistent product-group - component/issue to the table
            for prod in prods:
                
                if prod.strip()!=compCodeProdCodeMap[c.strip(), compCode.strip(), prodCode]:                
                    newPCcode['Product_Line (GCRM_PARENT_PROD_DESC)'] += [prod]
                    newPCcode['Group_Code (PROD_GROUP_CD)'] += [prodCode]
                    newPCcode['comp_id'] += [compCode]
                    newPCcode['Component'] += [caseReturnComponents[c.strip()]]
                    
                if prod.strip()!=issueCodeProdCodeMap[i.strip(), issueCode.strip(), prodCode]:
                    newPIcode['Product_Line'] += [prod]
                    newPIcode['Group_Code'] += [prodCode]
                    newPIcode['Issue_Cd'] += [issueCode]
                    newPIcode['Issue'] += [caseReturnIssues[i.strip()]]

            newPCIS['AffectedProduct'] += [affProd]
            newPCIS['EligibleProduct'] += [affProd]
            newPCIS['Component'] += [caseReturnComponents[c.strip()]]
            newPCIS['CaseIssue'] += [caseReturnIssues[i.strip()]]
            newPCIS['Symptoms'] += [s.strip()]
            newPCIS['Column'] += ['PROPAGATED']

df_ = pd.DataFrame(newPCIS)
df_['Markdown'] = ''
df_['Keywords'] = ''
df_['Original Descriptions (removed 5/31)'] = ''
df_['Symptom Char Count (79 char limit)'] = ''
df_['Description'] = ''

newDict = pd.concat([dict_, df_])
newDict.drop_duplicates(list(newDict.columns), inplace=True)
newDict = newDict[['Markdown','EligibleProduct','AffectedProduct','Component','CaseIssue','Symptoms','Column',
                   'Description','Keywords','Original Descriptions (removed 5/31)',
                   'Symptom Char Count (79 char limit)']]
newDict.to_csv(EXPANDED_DICT_ADDRESS + ".csv", index=False)
newDict.to_excel(EXPANDED_DICT_ADDRESS + ".xlsx", index=False)

print("The dimensions of the expanded dictionary are: ", newDict.shape)

newPCcode = pd.DataFrame(newPCcode)
newPCcode['Column'] = 'PROPAGATED'
newComp = pd.concat([compCodes, newPCcode])
newComp.drop_duplicates(list(newComp.columns), inplace=True)
newComp = newComp[['Product_Line (GCRM_PARENT_PROD_DESC)', 'Group_Code (PROD_GROUP_CD)', 'comp_id', 'Component',
                   'Column']]
newComp.to_csv(EXPANDED_COMPS_ADDRESS + ".csv", index=False)
newComp.to_excel(EXPANDED_COMPS_ADDRESS + ".xlsx", index=False)

newPIcode = pd.DataFrame(newPIcode)
newPIcode['Column'] = 'PROPAGATED'
newIssue = pd.concat([issueCodes, newPIcode])
newIssue.drop_duplicates(list(newIssue.columns), inplace=True)
newIssue = newIssue[['Product_Line', 'Group_Code', 'Issue_Cd', 'Issue', 'Column']]
newIssue.to_csv(EXPANDED_ISSUES_ADDRESS + ".csv", index=False)
newIssue.to_excel(EXPANDED_ISSUES_ADDRESS + ".xlsx", index=False)

END = time()
print("Finished expanding the dictionary. Time spent: %s minutes.\n" % str(round((END - START) / 60, 2)))



