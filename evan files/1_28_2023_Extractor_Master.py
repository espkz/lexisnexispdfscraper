#!/usr/bin/env python
# coding: utf-8

# In[29]:


import os,sys,subprocess
import tempfile
from fuzzywuzzy import fuzz
import pdftotext

#to user- modify this to the path of your pdftotext.exe
PDFTOTEXT_PATH="C:\\Users\\evany_cdhq038\\OneDrive\\Desktop\\Economics_Research\\xpdf-tools-win-4.03\\bin64\\pdftotext.exe"

results=[]
completeARList=[]
completeDRList=[]
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
                
            
            #extraction process below
            
            #Extracts gender
            counter=0
            while counter<len(lineArray):
                if("Gender" in lineArray[counter]):
                    if("DOB" in lineArray[counter]):
                        gender=lineArray[counter+1][lineArray[counter].find("Gender"):lineArray[counter].find("LexID")]
                        addThis["Gender"]= gender
                counter=counter+1
            
            #extracts SSN by alternate method through voter registration
            SSNCounter=0
            RegistrantLine=0
            VoterLine=0
            while SSNCounter<len(lineArray):
                if("Registrant Information" in lineArray[SSNCounter]):
                    RegistrantLine=SSNCounter
                if("Voter Information" in lineArray[SSNCounter]):
                    VoterLine=SSNCounter
                SSNCounter+=1
            newLoop=RegistrantLine
            while(newLoop<=VoterLine):
                if("SSN" in lineArray[newLoop]):
                    SSN=lineArray[newLoop][lineArray[newLoop].find(":")+1:]
                    addThis["SSN"]=SSN.strip()
                newLoop+=1
            
            #extracts emails
            emailMax=6
            emailCounter=0
            while emailCounter<len(lineArray):
                if("Email" in lineArray[emailCounter]):
                    if("SSN" in lineArray[emailCounter]):
                        i=1
                        while i<=emailMax:
                            emailNum= "Email"+str(i)
                            emailHolder=lineArray[emailCounter+i][lineArray[emailCounter].find("Email"):]
                            if(emailHolder[-1:] == "\n"):
                                emailHolder=emailHolder[:-1]
                            addThis[emailNum]=emailHolder
                            i=i+1
                emailCounter=emailCounter+1
            
            #extracts date of birth month and year 
            DOBcounter=0
            while DOBcounter<len(lineArray):
                if("DOB" in lineArray[DOBcounter]):
                    if("SSN" in lineArray[DOBcounter] and "Gender" in lineArray[DOBcounter]):
                        DOB=lineArray[DOBcounter+2][lineArray[DOBcounter].find("DOB"):lineArray[DOBcounter].find("Gender")]
                DOBcounter=DOBcounter+1
            DOBMonth=DOB[:DOB.find("/")]
            DOBYear=DOB[DOB.find("/")+1:]
            addThis["DOBMonth"]=DOBMonth
            addThis["DOBYear"]=DOBYear.strip()
            
            #extracts lexID
            IDCounter=0
            while IDCounter<len(tableFile):
                if("LexID" in tableFile[IDCounter]):
                    if("Email" in tableFile[IDCounter]):
                        lexID=tableFile[IDCounter+2][tableFile[IDCounter].find("LexID"):tableFile[IDCounter].find("Email")]
                        addThis["LexID"]=lexID.strip()
                IDCounter=IDCounter+1
            
            #Extracting current address and county
            endCounter=0
            endpoint=0
            while endCounter<len(lineArray):
                if("ADDITIONAL PERSONAL INFORMATION" in lineArray[endCounter]):
                    endpoint=endCounter
                endCounter+=1
            addyCounter=0
            while addyCounter<len(lineArray):
                if("Address" in lineArray[addyCounter]):
                    if("County" in lineArray[addyCounter] and "Phone" in lineArray[addyCounter]):
                        a=1
                        currentAddress=''
                        b=endpoint-addyCounter-1
                        lineCounter=0
                        while a <= b: 
                            currentAddress+=lineArray[addyCounter+a][lineArray[addyCounter].find("Address"):lineArray[addyCounter].find("County")].strip()
                            if lineArray[addyCounter+a][lineArray[addyCounter].find("Address"):lineArray[addyCounter].find("County")].strip() != '':
                                currentAddress+=" "
                                lineCounter+=1
                                if "COUNTY" in lineArray[addyCounter+a]:
                                    addThis["County"]=lineArray[addyCounter+a][lineArray[addyCounter].find("Address"):lineArray[addyCounter].find("County")].strip()
                            a+=1
                addyCounter+=1
            try:
                addThis["CurrentAddress"]= currentAddress.replace(addThis["County"],"").strip()
            except:
                print("No COUNTY for "+  fileName.name)
            #extracts phone number
            phoneCounter=0
            while phoneCounter<len(lineArray):
                if("Phone" in lineArray[phoneCounter]):
                    if("County" in lineArray[phoneCounter] and "Address" in lineArray[phoneCounter]): #makes sure it is the beginning record page
                        phoneNum=lineArray[phoneCounter+1][lineArray[phoneCounter].find("Phone"):]
                phoneCounter=phoneCounter+1
            addThis["PhoneNumber"]=phoneNum.strip()
            
            #extracting name
            addThis["FirstName"]=addThis["PDFName"][:addThis["PDFName"].find("_")].strip()
            addThis["LastName"]=addThis["PDFName"][addThis["PDFName"].find("_")+1:-4].strip()
            addThis["FullName"]=addThis["FirstName"]+' ' + addThis["LastName"]
            
            #extracts property addresses and date range section
            
            #3/26/23 note- This is the section you would need to modify in order to fix the date range issue
            addressCounter=0
            while addressCounter<len(tableFile):
                if("Address Summary" in tableFile[addressCounter]):
                    numAddresses=tableFile[addressCounter][tableFile[addressCounter].find("-")+1:tableFile[addressCounter].find("records")]
                    numAddresses=int(numAddresses)
                addressCounter+=1
            beginCounter=0
            startPoint=0
            while beginCounter<len(tableFile):
                if("Address Details" in tableFile[beginCounter]):
                    startPoint=beginCounter
                beginCounter+=1
            k=1
            searchThis=str(k)+":"
            addyArray=[]
            dateArray=[]
            while startPoint<len(tableFile):
                if searchThis in tableFile[startPoint]:
                    addressHolder=tableFile[startPoint][2:]
                    if("Dates" in addressHolder):
                        addressHolder=addressHolder[:addressHolder.find("Dates")]
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')  
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addressHolder=addressHolder.replace("  ",' ')
                    addyArray.append(addressHolder.strip())
                    k+=1
                    if k>numAddresses:
                        k='null'
                    searchThis=str(k)+":"
            
                if("Dates" in tableFile[startPoint] and "Phone" in tableFile[startPoint]):
                    dateRange=tableFile[startPoint+2][tableFile[startPoint].find("Dates"):tableFile[startPoint].find("Phone")] #goes down one line and takes date range, might be blank
                    dateArray.append(dateRange.strip())
        
                startPoint+=1
            e=0
            addressRangeList=[]
            while e<len(addyArray):
                holdingDict={}
                holdingDict["PropertyAddress"]=addyArray[e].replace(":","").strip()
                holdingDict["PropertyAddress"]=holdingDict["PropertyAddress"].strip()
                try:
                    holdingDict["DateRange"]=dateArray[e]
                except:
                    print("DateRange error on "+ fileName.name)
                addressRangeList.append(holdingDict)
                e+=1
            fullAnalystAddressList=[]
            for tempDict in addressRangeList:
                tempHolder={**addThis,**tempDict}
                fullAnalystAddressList.append(tempHolder)
            
            results=results + fullAnalystAddressList
    
             #Assessment Record and Deed Record Section
            tempCounter=0
            assessmentStart=0
            assessmentEnd=0
    
            firstInstance=True
            firstEndInstance=True
            while tempCounter < len(lineArray):
                if("Assessment Record" in lineArray[tempCounter] or "Deed Record" in lineArray[tempCounter]):
                    if firstInstance: 
                        assessmentStart=tempCounter
                        firstInstance= False
                tempCounter+=1
            tempCounter=0
            while tempCounter < len(lineArray):
                if("Boats - " in lineArray[tempCounter] or "Potential Relatives -" in lineArray[tempCounter]):
                    if firstEndInstance and tempCounter>assessmentStart:
                        assessmentEnd=tempCounter
                        firstEndInstance= False
                tempCounter+=1
            
            recordDict={}
            i=1
            assessmentRecords=[]
            deedRecords=[]
            count=assessmentStart
            search=str(i)+ ":"
            while count<assessmentEnd:
                if(search in lineArray[count]):
                    if(lineArray[count][lineArray[count].find(search)+2:lineArray[count].find("Record")].strip()=="Assessment"):
                        #assessment records
                        addThis2={} 
                        endpoint=count+1
                        while lineArray[endpoint].find("Record for")==-1 and lineArray[endpoint].find("Boat")==-1 and lineArray[endpoint].find("Potential Relatives")==-1:# returns -1 if not found, loops until it finds "Record for"
                            endpoint+=1
                        recordDict["Assessment"+str(search)]=[]
                        temp=count
                        while temp<endpoint:
                            if("Address" in lineArray[temp]):
                                addThis2["ARAddress"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("County" in lineArray[temp]):
                                addThis2["ARCounty"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Recording Date" in lineArray[temp]):
                                addThis2["ARRecordingDate"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Sale Date" in lineArray[temp]):
                                addThis2["ARSaleDate"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Sale Price" in lineArray[temp]):
                                addThis2["ARSalePrice"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Assessed Value" in lineArray[temp]):
                                addThis2["ARAssessedValue"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Market Land Value" in lineArray[temp]):
                                addThis2["ARMarketLandValue"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Market Improvement Value" in lineArray[temp]):
                                addThis2["ARMarketImprovementValue"]= lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Total Market Value" in lineArray[temp]):
                                addThis2["ARTotalMarketValue"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            temp+=1      
                        assessmentRecords.append(addThis2)
                    if(lineArray[count][lineArray[count].find(search)+2:lineArray[count].find("Record")].strip()=="Deed"):
                        addThis3={}
                        endpoint=count+1
                        while(lineArray[endpoint].find("Record for")==-1 and lineArray[endpoint].find("Boat")==-1 and lineArray[endpoint].find("Potential Relatives")==-1):# returns -1 if not found, loops until it finds "Record for"
                            endpoint+=1
                        recordDict["Deed"+str(search)]=[]
                        temp=count
                        while temp<endpoint:
                            if("Address" in lineArray[temp]):
                                addThis3["DRAddress"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Contract Date" in lineArray[temp]):
                                addThis3["DRContractDate"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Recording Date" in lineArray[temp]):
                                addThis3["DRRecordingDate"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Loan Amount" in lineArray[temp]):
                                addThis3["DRLoanAmount"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Loan Type" in lineArray[temp]):
                                addThis3["DRLoanType"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Title Company" in lineArray[temp]):
                                addThis3["DRTitleCompany"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Transaction Type" in lineArray[temp]):
                                addThis3["DRTransactionType"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Description" in lineArray[temp]):
                                addThis3["DRDescription"]=lineArray[temp][lineArray[temp].find(":")+1:].strip()
                            if("Lender Information" in lineArray[temp]):
                                addThis3["DRLenderInformation"]=lineArray[temp+1].find(":")+1
                            temp+=1
                        deedRecords.append(addThis3)
                    i+=1
                    search=str(i)+":"
                count+=1
            cleanAR=[]
            cleanDR=[]

            a=0
            while a<len(assessmentRecords):
                base=assessmentRecords[a]
                b=a+1
                while b<len(assessmentRecords)-a:
                    comparison=assessmentRecords[b]
                    ratio=fuzz.ratio(base["ARAddress"].lower(),comparison["ARAddress"].lower())
                    if(ratio>80): #levenhstein ration >80
                        agregaEsto={**base,**comparison}
                        cleanAR.append(agregaEsto)
                    b+=1
                a+=1
            a=0
            while a<len(deedRecords):
                base=deedRecords[a]
                b=a+1
                while b<len(deedRecords)-a:
                    comparison=deedRecords[b]
                    ratio=fuzz.ratio(base["DRAddress"].lower(),comparison["DRAddress"].lower())
                    if(ratio>80): #levenhstein ration >80
                        agregaEsto={**base,**comparison}
                        cleanDR.append(agregaEsto)
                    b+=1
                a+=1
            if(len(cleanAR)==0):
                cleanAR=assessmentRecords
            if(len(cleanDR)==0):
                cleanDR=deedRecords
    
            for thing in cleanAR:
                addAR={**addThis,**thing}
                completeARList.append(addAR)
            
            for thing in cleanDR:
                addDR={**addThis,**thing}
                completeDRList.append(addDR)
            


# In[30]:


#cleaning section for property addresses
#remove dates and phone numbers
import re
cleanedPropertyAddresses=[]
for uncleanAddy in results:
    zipMatch=re.search('.*\s\d{5}(-\d{4})?',uncleanAddy["PropertyAddress"])
    if zipMatch is not None:
        #print(uncleanAddy["PropertyAddress"] +"  ====cleaned to====  "+ uncleanAddy["PropertyAddress"][:zipMatch.end()].strip())
        remainder =uncleanAddy["PropertyAddress"][zipMatch.end():].strip()
        if "(" in remainder:
            uncleanAddy["PhoneNumber"]=remainder[remainder.find("("):]
            uncleanAddy["DateRange"]= remainder[:remainder.find("(")]
        else:
            #phoneMatch=re.search('.*\s\d{3}-\d{4}?',remainder)
            #if phoneMatch is not None:
                #print(phoneMatch.end())
                #print(remainder[phoneMatch.start():])
                #print(remainder[:phoneMatch.start()])
             #   uncleanAddy["PhoneNumber"]= remainder[phoneMatch.end():]
              #  uncleanAddy["DateRange"]= remainder[:phoneMatch.end()]
            uncleanAddy["DateRange"] =uncleanAddy["PropertyAddress"][zipMatch.end():].strip()
        
        uncleanAddy["PropertyAddress"]=uncleanAddy["PropertyAddress"][:zipMatch.end()].strip()
    


# In[31]:


#exporting to csv
import csv
csv_columns=["PDFName", "FullName", "FirstName", "LastName","County","PhoneNumber","SSN","DOBMonth","DOBYear","Gender","LexID","Email1","Email2","Email3","Email4","Email5","Email6","CurrentAddress","PropertyAddress","DateRange"]
AR_columns=["ARAddress","ARCounty","ARRecordingDate","ARSaleDate","ARSalePrice","ARAssessedValue","ARMarketLandValue","ARMarketImprovementValue","ARTotalMarketValue"]
DR_columns=["DRAddress","DRContractDate","DRRecordingDate","DRLoanAmount","DRLoanType","DRTitleCompany","DRTransactionType","DRDescription","DRLenderInformation"]
all_columns=csv_columns+AR_columns+DR_columns

masterList=[]

for addyDict in results:
    mergeThis={}
    for ARDict in completeARList:
        tempRatio= fuzz.ratio(ARDict["ARAddress"].lower().strip(),addyDict["PropertyAddress"].lower().strip())
        if tempRatio> 90:
            addyDict={**addyDict,**ARDict} 
            
    for DRDict in completeDRList:
        holdingRatio= fuzz.ratio(DRDict["DRAddress"].lower().strip(),addyDict["PropertyAddress"].lower().strip())
        if holdingRatio>90:
            addyDict={**addyDict,**DRDict}
    
    masterList.append(addyDict)
    
    
csv_file="2_13_Moody.csv"
masterList=sorted(masterList,key=lambda x: x['FirstName'])
    
try:
    with open(csv_file,'w',newline="") as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=all_columns)
        writer.writeheader()
        for data in masterList:
            writer.writerow(data)
except IOError:
    print("IOError")


# In[ ]:





# In[ ]:




