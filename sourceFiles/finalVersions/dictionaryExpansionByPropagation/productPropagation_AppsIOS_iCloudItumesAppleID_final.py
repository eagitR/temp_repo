
"""
Created on Aug 1, 2016

@author: eliyarasgarieh
________________________________________________________________________________

Short script for symptom propagation based on Josh's request.

Inputs:
- symptom-classification file in .xlsx format
- Product group mapping file in .xlsx format

Outputs:
- The expanded dictionary by propagation in .csv and .xlsx formats

"""

import pandas as pd
import sys
import os
from time import time

ALL_START = time()

args = sys.argv

DICT_ADDRESS = args[1]
PROD_MAPPING = args[2]

SOURCE = "."
NEW_DICT_DEST = os.path.join(SOURCE, "symptomClassification_propagated_Aug29")

#______________________________________________________________________________________________________________________#
# Loading dictionary and product groups for expansion

dictNew_ = pd.read_excel(DICT_ADDRESS)
prodGroups = pd.read_excel(PROD_MAPPING)
allProds = set([x.strip() for x in prodGroups['PRODUCT NAME']])

#______________________________________________________________________________________________________________________#
# Propagating all the Symptoms and CaseIssue values for Apps component and iOS devices.
print('\n', '-' * 100)
print("Propagating products for Apps component between ios devices ...")

def appProp(x, iosProducts):
    # Finding the SI combinations that should be added to tbe current iOS EligibleProduct-AffectedProduct group
    # and propagating the non-existent combinations

    propData = {'AffectedProduct': [],
                'EligibleProduct': [],
                'Column': []
                }

    grpProds = set(x['AffectedProduct'])
    for prod in (iosProducts - grpProds):
        propData['AffectedProduct'].append(prod)
        propData['EligibleProduct'].append(prod)
        propData['Column'].append('PROPAGATED(Apps_iOS)')

    return pd.DataFrame(propData)

# Loading and saving eligible ios products
iosProds = set(prodGroups['PRODUCT NAME'].loc[[('ipad' in p.lower()) or
                            ('iphone' in p.lower()) or
                            ('ipod' in p.lower())
                            for p in prodGroups['PRODUCT NAME']]])
iosProds.remove('SMART KEYBOARD FOR IPAD PRO 12.9-INCH')
iosProds.remove('SMART KEYBOARD FOR IPAD PRO 9.7-INCH')
iosProds.remove('iPhone 6s Smart Battery Case')
iosProds.remove('iPhone Configuration Utility (Mac)')
iosProds.remove('VIN, IPAD 3G')
iosProds.remove('OBS IPHONE')


dataApps = dictNew_.loc[dictNew_.Component == 'Apps', :]
dataAppsIOS = dataApps.loc[[p in iosProds for p in dataApps.AffectedProduct], :]
dataProp_iOS = dataAppsIOS.groupby(['Symptoms', 'CaseIssue', 'Component']).apply(appProp, iosProds)
dataProp_iOS.reset_index(inplace=True)

# ______________________________________________________________________________________________________________________#
# Propagating all SCIs related to Apple ID-iCloud-iTunes
print('\n', '-' * 100)
print("Propagating products iCloud, iTunes, Apple ID ...")

def apIcItProp(x, apIcItProducts):
    # Finding the SI combinations that should be added to tbe current iOS EligibleProduct-AffectedProduct group
    # and propagating the non-existent combinations

    propData = {'EligibleProduct': [],
                'Column': []
                }

    grpProds = set(x['EligibleProduct'])
    for prod in (apIcItProducts - grpProds):
        propData['EligibleProduct'].append(prod)
        propData['Column'].append('PROPAGATED(AppleID_iCloud_iTunes)')

    return pd.DataFrame(propData)
dataAppID_iC_iT = dictNew_.loc[[('apple id' in p.lower()) or
                                ('icloud' in p.lower()) or
                                ('itunes' in p.lower())
                            for p in dictNew_.AffectedProduct], :]
dataAppID_iC_iT = dataAppID_iC_iT.loc[['iTunes Store'.lower() not in p.lower()
                                       for p in dataAppID_iC_iT.AffectedProduct], :]
apIcItProds = set([x.strip() for x in dataAppID_iC_iT.EligibleProduct if x.strip() in allProds])
dataProp_aii = dataAppID_iC_iT.groupby(['Symptoms', 'CaseIssue', 'Component', 'AffectedProduct']).apply(apIcItProp,
                                                                                                        apIcItProds)
dataProp_aii.reset_index(inplace=True)

# Expanding the dictionary
dictExpanded = pd.concat([dictNew_, dataProp_iOS, dataProp_aii])
dictExpanded.drop_duplicates(inplace=True)
dictExpanded = dictExpanded[dictNew_.columns]
dictExpanded.to_excel(NEW_DICT_DEST + ".xlsx", index=False)
dictExpanded.to_csv(NEW_DICT_DEST + ".csv", index=False)

END = time()

#______________________________________________________________________________________________________________________#
ALL_END = time()

print('\n', '-'*100)
print("Dictionary expansion by propagation finished. Total time spent: %s minutes.\n" %
      str(round((ALL_END - ALL_START)/60, 2)))



