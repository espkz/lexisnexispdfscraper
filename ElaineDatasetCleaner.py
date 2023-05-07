#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import pandas as pd

df1 = pd.read_excel(r"C:\Users\evany_cdhq038\OneDrive\Desktop\1_21_2023_Lexus\Moody's LinkedIn Analysts Sets 1+2.xlsx", sheet_name='Moodys LinkedIn Analysts 1')
#df2 = pd.read_excel(r"C:\Users\evany_cdhq038\OneDrive\Desktop\1_21_2023_Lexus\Moody's LinkedIn Analysts Sets 1+2.xlsx", sheet_name='Moodys LinkedIn Analysts 2')


# In[2]:


#cleaning dfs to remove LexusMatch of 0
#df1 = df1[df1['lexismatch'] == 1.0]
#df2 = df2[df2['lexismatch'] == 1.0]
oneDF=df1[df1['lexismatch'] == 1.0]
zeroDF=df1[df1['lexismatch'] != 1.0]


# In[4]:


#fuzzy matching to pdfname
from fuzzywuzzy import fuzz
#value = fuzz.ratio('New York', 'New York')
analystNames= oneDF["Analyst"]
cleanedAnalystNames=[]
purePDFNames=[]
#cleanedPDFNames=[]
correspondingPDFs=[]
correspondingMatchRatio=[]
pdfMatch=[]

import os
root = "C:\\Users\\evany_cdhq038\\OneDrive\\Desktop\\1_21_2023_Lexus\\Elaine Han Moody's Lexis Nexis PDFs Sets 1+2"
for entry in os.scandir(root):
    purePDFNames.append(entry.name)
    #cleanedPDFNames.append(entry.name[:-4].replace("_", " "))
    
#removing some extra files
purePDFNames.pop(0) #removes ipynb checkpoint
purePDFNames.pop(0) #removes program in the folder

#cleaning
for dirtyName in analystNames:
    dirtyName=dirtyName.replace(",","")
    dirtyName=dirtyName.replace("CFA","")
    dirtyName=dirtyName.replace("(","")
    dirtyName=dirtyName.replace(")","")
    cleanedAnalystNames.append(dirtyName)
    
#splitting into first and last name
#finding the one with the highest geometric average
for name in cleanedAnalystNames:
    name=name.strip()
    firstName=name[:name.find(" ")].strip().lower()
    lastName=name[name.rfind(" "):].strip().lower()
    print(firstName+" : "+ lastName)
    firstNameRatio=1
    lastNameRatio=1
    highestMatchValue=0
    highestMatchIndex=0
    
    i=0
    while i<len(purePDFNames):
        PDF=purePDFNames[i]
        first=PDF[:PDF.find("_")].strip().lower()
        last=PDF[PDF.find("_")+1:PDF.find(".")].strip().lower()
        
        firstNameRatio=fuzz.ratio(first,firstName)
        lastNameRatio=fuzz.ratio(last,lastName)
        if firstNameRatio==0:
            firstNameRatio+=1
            
        if lastNameRatio==0:
            lastNameRatio+=1
            
        geomAvg=(int(firstNameRatio)*int(lastNameRatio))/(int(firstNameRatio)+int(lastNameRatio))
        if geomAvg>highestMatchValue:
            highestMatchValue=geomAvg
            highestMatchIndex=i
        i+=1
        
    
    correspondingPDFs.append(purePDFNames[highestMatchIndex])
    correspondingMatchRatio.append(highestMatchValue)
    


#oneDF["PDFMatch>=80"]=pdfMatch
oneDF["correspondingPDF"]=correspondingPDFs
oneDF["correspondingMatchRatio"]=correspondingMatchRatio

oneDF=oneDF.sort_values(by='correspondingMatchRatio', ascending=False)
columnHeaders=['mdanid', 'lexismatch','Analyst','correspondingPDF','correspondingMatchRatio','linkedin_url','linkedin_title','Group','office','gender','mis_years?','first_job_start_year','grad_instit','grad_degree','grad_year','ug_instit','ug_year','comments','Division','Country','namelen','linkedin_name','title','moody_start','moody_end','source']
oneDF = oneDF[columnHeaders]


# In[5]:


import openpyxl
#exporting data to excel

oneDF.to_excel("2_15_EvanMoody1.xlsx")


# In[6]:


zeroDF.to_excel("2_15_EvanMoody0.xlsx")


# In[ ]:




