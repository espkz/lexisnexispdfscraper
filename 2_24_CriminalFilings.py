#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os,sys,subprocess
import tempfile
from fuzzywuzzy import fuzz
PDFTOTEXT_PATH="C:\\Users\\evany_cdhq038\\OneDrive\\Desktop\\Economics_Research\\xpdf-tools-win-4.03\\bin64\\pdftotext.exe"
#PDFTOTEXT_PATH="C:\\Users\\evany_cdhq038\\OneDrive\\Desktop\\1_21_2023_Lexus\\pdftotext.exe"

results=[]
for fileName in os.scandir():
        if fileName.is_file() and fileName.name.endswith(".pdf"):
            addThis={}
            addThis["PDFName"]=fileName.name
            print(fileName.name)
            
            pdfPath=fileName.path
            #getting -layout version and storing as pdfTextLayout
            try:
                q = subprocess.Popen([PDFTOTEXT_PATH,'-layout',pdfPath,"-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
                pdfTextLayout, err = q.communicate()
            except:
                print('pdftotext Layout failed')
            #getting -table version and storign as pdfTextTable
            try:
                q = subprocess.Popen([PDFTOTEXT_PATH,'-table',pdfPath,"-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
                pdfTextTable, err = q.communicate()
            except:
                print('pdftotext Table failed')
                
            #writing a tempfile for bot _table and _layout format
            #this is because the old code is based off of f.readlines()
            f = tempfile.TemporaryFile()
            try:
                f.write(pdfTextLayout)
                f.seek(0)
                encodedlineArray=f.readlines() #lineArray is -layout format and what we will be extracting primarily from
            except:
                print("Temp file creation for Layout error")
            finally:
                f.close()
            
            g=tempfile.TemporaryFile()
            try:
                g.write(pdfTextTable)
                g.seek(0)
                encodedtableFile=g.readlines()
            except:
                print("Temp file creation for Table error")
            finally:
                g.close()
            
            #decoding both from bytes to string- might need some modifications bc of latin1 decoding
            lineArray=[]
            tableFile=[]
            for line in encodedlineArray:
                lineArray.append(line.decode("Latin1"))
                
            for line in encodedtableFile:
                tableFile.append(line.decode("Latin1"))
            
            #voter registration extraction below
            lineCounter=0
            while lineCounter<len(lineArray):
                if ":" in lineArray[lineCounter] and "Court Report" in lineArray[lineCounter]:
                    agregaEsto={}
                    agregaEsto["PDFName"]=addThis["PDFName"]
                    i=lineCounter+1
                    while i<len(lineArray):
                        if("Case Filing Date" in lineArray[i]):
                            agregaEsto["CaseFilingDate"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Offense Date" in lineArray[i]):
                            agregaEsto["OffenseDate"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Categories" in lineArray[i]):
                            agregaEsto["Categories"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Case Type" in lineArray[i]):
                            agregaEsto["CaseType"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Court Offense" in lineArray[i]):
                            agregaEsto["CourtOffense"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Court Disposition" in lineArray[i] and "Date" not in lineArray[i]):
                            agregaEsto["CourtDisposition"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        
                        if ":" in lineArray[i] and "Court Report" in lineArray[i]:
                            break
                        if "Cellular & Alternate Phones" in lineArray[i]:
                            break
                        
                        i+=1
                    print(agregaEsto)
                    results.append(agregaEsto)
                        
                lineCounter+=1
            


# In[2]:


import csv
csv_file="2_28_MoodysCriminalReports.csv"
#masterList=sorted(results,key=lambda x: x['PDFName'])
all_columns=["PDFName","CaseFilingDate","OffenseDate","Categories","CaseType","CourtOffense","CourtDisposition"]
    
try:
    with open(csv_file,'w',newline="") as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=all_columns)
        writer.writeheader()
        for data in results:
            writer.writerow(data)
except IOError:
    print("IOError")


# In[ ]:




