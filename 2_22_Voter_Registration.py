#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os,sys,subprocess
import tempfile
from fuzzywuzzy import fuzz
#to user- modify to your pdftotext.exe path
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
            #3/26/23 Note- you need to add if-statements below to extract the other information Professor Lock wants you to do
            lineCounter=0
            while lineCounter<len(lineArray):
                if ":" in lineArray[lineCounter] and "Voter Registration" in lineArray[lineCounter]:
                    agregaEsto={}
                    agregaEsto["PDFName"]=addThis["PDFName"]
                    i=lineCounter+1
                    while i<len(lineArray):
                        if("Registration Date" in lineArray[i]):
                            agregaEsto["RegistrationDate"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Last Vote Date" in lineArray[i]):
                            agregaEsto["LastVoteDate"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Party Affiliation" in lineArray[i]):
                            agregaEsto["PartyAffiliation"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        if("Active Status" in lineArray[i]):
                            agregaEsto["ActiveStatus"]=lineArray[i][lineArray[i].find(":")+1:].strip()
                        
                        if ":" in lineArray[i] and "Voter Registration" in lineArray[i]:
                            break
                        if "Professional Licenses" in lineArray[i]:
                            break
                        
                        i+=1
                    print(agregaEsto)
                    results.append(agregaEsto)
                        
                lineCounter+=1
            


# In[2]:


#exporting to csv
import csv
csv_file="2_27_VoterRegistrationMoody.csv"
masterList=sorted(results,key=lambda x: x['PDFName'])
all_columns=["PDFName","RegistrationDate","PartyAffiliation","ActiveStatus","LastVoteDate"]
    
try:
    with open(csv_file,'w',newline="") as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=all_columns)
        writer.writeheader()
        for data in masterList:
            writer.writerow(data)
except IOError:
    print("IOError")


# In[ ]:




