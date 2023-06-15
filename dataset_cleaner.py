#!/usr/bin/env python
# coding: utf-8

# What's supposed to be in the columns? additonal information, or just name, corresponding pdf, and score?


import os
import sys
import pandas as pd
from fuzzywuzzy import fuzz
import openpyxl

df1 = pd.read_excel("Merged Analyst Documents - Lexis Nexis + LinkedIn/Moodys Lexis Nexis-LinkedIn Analysts - Sets 1+2 - Kushagra, Anna, Ellie Merged.xlsx")

oneDF = df1[df1['lexisfmatch'] == 1.0]
zeroDF = df1[df1['lexisfmatch'] != 1.0]

# In[4]:


# value = fuzz.ratio('New York', 'New York')
analystNames = oneDF["analyst"]
cleanedAnalystNames = []
purePDFNames = []
# cleanedPDFNames=[]
correspondingPDFs = []
correspondingMatchRatio = []
pdfMatch = []

root = "Merged Analyst Documents - Lexis Nexis + LinkedIn/Moodys Analyst PDFs"
for entry in os.scandir(root):
    purePDFNames.append(entry.name)
    # cleanedPDFNames.append(entry.name[:-4].replace("_", " "))



# cleaning
for dirtyName in analystNames:
    dirtyName = dirtyName.replace(",", "")
    dirtyName = dirtyName.replace("CFA", "")
    dirtyName = dirtyName.replace("(", "")
    dirtyName = dirtyName.replace(")", "")
    cleanedAnalystNames.append(dirtyName)

# splitting into first and last name
# finding the one with the highest geometric average
for name in cleanedAnalystNames:
    name = name.strip()
    firstName = name[:name.find(" ")].strip().lower()
    lastName = name[name.rfind(" "):].strip().lower()
    # print(firstName + " : " + lastName)
    firstNameRatio = 1
    lastNameRatio = 1
    highestMatchValue = 0
    highestMatchIndex = 0

    i = 0
    while i < len(purePDFNames):
        PDF = purePDFNames[i]
        first = PDF[:PDF.find("_")].strip().lower()
        last = PDF[PDF.find("_") + 1:PDF.find(".")].strip().lower()

        firstNameRatio = fuzz.ratio(first, firstName)
        lastNameRatio = fuzz.ratio(last, lastName)
        if firstNameRatio == 0:
            firstNameRatio += 1

        if lastNameRatio == 0:
            lastNameRatio += 1

        geomAvg = (int(firstNameRatio) * int(lastNameRatio)) / (int(firstNameRatio) + int(lastNameRatio))
        if geomAvg > highestMatchValue:
            highestMatchValue = geomAvg
            highestMatchIndex = i
        i += 1

    correspondingPDFs.append(purePDFNames[highestMatchIndex])
    correspondingMatchRatio.append(highestMatchValue)

# oneDF["PDFMatch>=80"]=pdfMatch
oneDF["correspondingPDF"] = correspondingPDFs
oneDF["correspondingMatchRatio"] = correspondingMatchRatio

oneDF = oneDF.sort_values(by='correspondingMatchRatio', ascending=False)
columnHeaders = ['analyst', 'correspondingPDF', 'correspondingMatchRatio']
oneDF = oneDF[columnHeaders]

# In[5]:

# exporting data to excel

oneDF.to_csv("MoodysNameMatch.csv")

# In[6]:


# zeroDF.to_excel("2_15_EvanMoody0.xlsx")

# In[ ]: