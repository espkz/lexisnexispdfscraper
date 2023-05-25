#!/usr/bin/env python
# coding: utf-8

# In[29]:


import os, sys, subprocess
import tempfile
from fuzzywuzzy import fuzz
import pdftotext
import re
import csv

# initialize a csv file

csv_file_name = "test" + ".csv"

csv_columns = ["PDFName", "FullName", "FirstName", "LastName", "County", "PhoneNumber", "SSN", "DOBMonth", "DOBYear",
               "Gender", "LexID", "Email1", "Email2", "Email3", "Email4", "Email5", "Email6", "CurrentAddress",
               "PropertyAddress", "DateRange"]

with open(csv_file_name, 'w') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(csv_columns)

f.close()

# to user- modify this to the path of your pdftotext.exe
PDFTOTEXT_PATH = '/usr/local/bin/pdftotext'
for fileName in os.scandir('pdfs'):
    if fileName.is_file() and fileName.name.endswith(".pdf"):
        information = {"PDFName": None, "FullName": None, "FirstName": None, "LastName": None, "County": None,
                       "PhoneNumber": None, "SSN": None, "DOBMonth": None, "DOBYear": None, "Gender": None,
                       "LexID": None, "Email1": None, "Email2": None, "Email3": None, "Email4": None, "Email5": None,
                       "Email6": None, "CurrentAddress": None, "PropertyAddress": {}, "ARRecords" : [], "DRRecords" : []}
        information["PDFName"] = fileName.name
        print(fileName.name)

        pdfPath = fileName.path
        # getting -layout version and storing as pdfTextLayout
        try:
            q = subprocess.Popen([PDFTOTEXT_PATH, '-f', '2', '-layout', pdfPath, "-"], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            pdfTextLayout, err = q.communicate()
        except:
            print('pdftotext Layout failed')

        # writing a tempfile for bot _table and _layout format
        # this is because the old code is based off of f.readlines()
        f = tempfile.TemporaryFile()
        try:
            f.write(pdfTextLayout)
            f.seek(0)
            encodedlineArray = f.readlines()  # lineArray is -layout format and what we will be extracting primarily from
        except:
            print("Temp file creation for Layout error")
        finally:
            f.close()

        new_name = fileName.name[:-4]

        with open('txts/' + new_name + '.txt', 'w') as f:
            f.write(str(pdfTextLayout, 'UTF-8'))
        f.close()


        # decoding both from bytes to string- might need some modifications bc of latin1 decoding
        contents = []
        tableFile = []
        for line in encodedlineArray:
            contents.append(line.decode("Latin1"))

        # extraction process below

        # Extracts gender and name and lexid and also dob
        counter = 0
        gender = "Male"
        names = []
        dates = []

        while counter < len(contents):
            lexid = re.findall("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", contents[counter])
            if len(lexid) != 0:
                information["LexID"] = lexid[0]
            if ("DOB" in contents[counter]):
                dates.append(contents[counter + 1].split())
            if ("Female" in contents[counter]):
                gender = "Female"
            if ("Full Name" in contents[counter]):
                names.append(contents[counter + 1].split())
            counter = counter + 1

        information["LastName"] = names[0][0][:-1]
        information["FirstName"] = names[0][1]
        if names[0][2].isalpha() and names[0][2].lower() != "po":
            information["FullName"] = information["FirstName"] + " " + names[0][2] + " " + information["LastName"]
        else:
            information["FullName"] = information["FirstName"] + " " + information["LastName"]

        information["DOBMonth"] = dates[0][1].split("/")[0]
        information["DOBYear"] = dates[0][1].split("/")[1]

        information["Gender"] = gender

        # extracts SSN
        SSNCounter = 0
        RegistrantLine = 0
        VoterLine = 0
        while SSNCounter < len(contents):
            if ("Registrant Information" in contents[SSNCounter]):
                RegistrantLine = SSNCounter
            if ("Voter Information" in contents[SSNCounter]):
                VoterLine = SSNCounter
            SSNCounter += 1
        newLoop = RegistrantLine
        while (newLoop <= VoterLine):
            if ("SSN" in contents[newLoop]):
                SSN = contents[newLoop][contents[newLoop].find(":") + 1:]
                information["SSN"] = SSN.strip()
            newLoop += 1

        # extracts emails
        emailMax = 6
        emailCounter = 0
        while emailCounter < len(contents):
            if ("Email" in contents[emailCounter]):
                if ("SSN" in contents[emailCounter]):
                    i = 1
                    while i <= emailMax:
                        emailNum = "Email" + str(i)
                        emailHolder = contents[emailCounter + i][contents[emailCounter].find("Email"):]
                        if (emailHolder[-1:] == "\n"):
                            emailHolder = emailHolder[:-1]
                        information[emailNum] = emailHolder
                        i = i + 1
            emailCounter = emailCounter + 1

        # Extracting current address and county
        endCounter = 0
        endpoint = 0
        while endCounter < len(contents):
            if ("ADDITIONAL PERSONAL INFORMATION" in contents[endCounter]):
                endpoint = endCounter
            endCounter += 1
        addyCounter = 0
        while addyCounter < len(contents):
            if ("Address" in contents[addyCounter]):
                if ("County" in contents[addyCounter] and "Phone" in contents[addyCounter]):
                    a = 1
                    currentAddress = ''
                    b = endpoint - addyCounter - 1
                    lineCounter = 0
                    while a <= b:
                        currentAddress += contents[addyCounter + a][
                                          contents[addyCounter].find("Address"):contents[addyCounter].find(
                                              "County")].strip()
                        if contents[addyCounter + a][
                           contents[addyCounter].find("Address"):contents[addyCounter].find("County")].strip() != '':
                            currentAddress += " "
                            lineCounter += 1
                            if "COUNTY" in contents[addyCounter + a]:
                                information["County"] = contents[addyCounter + a][
                                                        contents[addyCounter].find("Address"):contents[addyCounter].find(
                                                        "County")].strip()
                        a += 1
            addyCounter += 1
        try:
            information["CurrentAddress"] = currentAddress.replace(information["County"], "").strip()
        except:
            print("No COUNTY for " + fileName.name)
        # extracts phone number
        phoneCounter = 0
        while phoneCounter < len(contents):
            if ("Phone" in contents[phoneCounter]):
                if ("County" in contents[phoneCounter] and "Address" in contents[
                    phoneCounter]):  # makes sure it is the beginning record page
                    phoneNum = contents[phoneCounter + 1][contents[phoneCounter].find("Phone"):]
            phoneCounter = phoneCounter + 1
        information["PhoneNumber"] = phoneNum.strip()


        # extracts property addresses and date range section
        addressCounter = 0
        while addressCounter < len(contents):
            if ("Address Details" in contents[addressCounter]):
                break
            addressCounter += 1
        while addressCounter < len(contents):
            if ("Dates" in contents[addressCounter]):
                data1 = contents[addressCounter+1].split()
                if ("Page" in data1):
                    data1 = contents[addressCounter+4].split()
                data2 = contents[addressCounter+2]
                if ("Page" in data2.split()):
                    data2 = contents[addressCounter+5]
                date_range = ""
                # print(data1)
                # print(data2)
                if ("-" in data1):
                    pivot = data1.index("-")
                    date_range = data1[pivot-1] + "-" + data1[pivot+1]
                    data1 = data1[:pivot-1]
                # find if anything is at the end of data2
                end2 = re.split("\([0-9][0-9][0-9]\)", data2)[0].split()
                address = " ".join(data1) + " " +  " ".join(end2)
                information["PropertyAddress"][address] = date_range
            # end of address extraction
            if ("Voter Registration" in contents[addressCounter]):
                break
            addressCounter += 1

        # extracts property information (WIP)
        propertyCounter = 0
        while propertyCounter < len(contents):
            if ("Real Property" in contents[propertyCounter]):
                break
            propertyCounter += 1
        while propertyCounter < len(contents):
            if ("Assessment Record" in contents[propertyCounter]):
                assessmentKey = ""
                assessment = {"ARAddress": None, "ARCounty" : None, "ARRecordingDate" : None, "ARSaleDate" : None, "ARSalePrice" : None, "ARAssessedValue" : None, "ARMarketLandValue" : None, "ARMarketImprovementValue" : None, "ARTotalMarketValue" : None}
                assessmentCounter = propertyCounter + 1
                while (assessmentCounter < len(contents)):
                    # get county and address
                    if ("Address: " in contents[assessmentCounter]):
                        address = contents[assessmentCounter].split()
                        if (len(address) != 1):
                            assessment["ARAddress"] = " ".join(address[1:])
                    if ("County/FIPS:" in contents[assessmentCounter]):
                        county = contents[assessmentCounter].split()
                        assessment["ARCounty"] = " ".join(county[1:])

                    # get recording date
                    if ("Recording Date:" in contents[assessmentCounter]):
                        recordingdate = contents[assessmentCounter].split()
                        assessment["ARRecordingDate"] = recordingdate[-1]

                    # get sale date and price
                    if ("Sale Date:" in contents[assessmentCounter]):
                        saledate = contents[assessmentCounter].split()
                        assessment["ARSaleDate"] = saledate[-1]
                    if ("Sale Price:" in contents[assessmentCounter]):
                        saleprice = contents[assessmentCounter].split()
                        assessment["ARSalePrice"] = saleprice[-1]

                    # get values
                    if ("Assessed Value:" in contents[assessmentCounter]):
                        assessedvalue = contents[assessmentCounter].split()
                        assessment["ARAssessedValue"] = assessedvalue[-1]
                    if ("Market Land Value:" in contents[assessmentCounter]):
                        landvalue = contents[assessmentCounter].split()
                        assessment["ARMarketLandValue"] = landvalue[-1]
                    if ("Market Improvement Value:" in contents[assessmentCounter]):
                        improvvalue = contents[assessmentCounter].split()
                        assessment["ARMarketImprovementValue"] = improvvalue[-1]
                    if ("Total Market Value:" in contents[assessmentCounter]):
                        totalvalue = contents[assessmentCounter].split()
                        assessment["ARTotalMarketValue"] = totalvalue[-1]
                    # break
                    if ("Assessment Record" in contents[assessmentCounter] or "Deed Record" in contents[assessmentCounter]):
                        # print(assessment)
                        information["ARRecords"].append(assessment)
                        break
                    assessmentCounter += 1


            if ("Deed Record" in contents[propertyCounter]):
                deedKey = ""
                deed = {"DRAddress": None, "DRLenderName" : None, "DRContractDate" : None, "DRRecordingDate" : None, "DRLoanAmount" : None, "DRLoanType" : None, "DRTitleCompany" : None, "DRTransactionType" : None, "DRDescription" : None}
                deedCounter = propertyCounter + 1
                while (deedCounter < len(contents)):
                    # get address for key
                    if ("ddress:" in contents[deedCounter]):
                        deedKey = " ".join(contents[deedCounter].split()[1:])
                        deed["DRAddress"] = deedKey

                    # get lender name
                    if ("Lender Information" in contents[deedCounter]):
                        lendername = contents[deedCounter+1].split()
                        deed["DRLenderName"] = " ".join(lendername[1:])

                    # get dates
                    if ("Contract Date:" in contents[deedCounter]):
                        contractdate = contents[deedCounter].split()
                        deed["DRContractDate"] = contractdate[-1]
                    if ("Recording Date:" in contents[deedCounter]):
                        recordingdate = contents[deedCounter].split()
                        deed["DRRecordingDate"] = recordingdate[-1]

                    # get loan information
                    if ("Loan Amount:" in contents[deedCounter]):
                        loanamount = contents[deedCounter].split()
                        deed["DRLoanAmount"] = loanamount[-1]
                    if ("Loan Type:" in contents[deedCounter]):
                        loantype = contents[deedCounter].split()
                        deed["DRLoanType"] = " ".join(loantype[2:])

                    # other information
                    if ("Title Company:" in contents[deedCounter]):
                        titlecompany = contents[deedCounter].split()
                        deed["DRTitleCompany"] = " ".join(titlecompany[2:])

                    if ("Transaction Type:" in contents[deedCounter]):
                        transactiontype = contents[deedCounter].split()
                        deed["DRTransactionType"] = " ".join(transactiontype[2:])

                    if ("Description:" in contents[deedCounter]):
                        description = contents[deedCounter].split()
                        deed["DRDescription"] = " ".join(description[1:])


                    # break
                    if ("Assessment Record" in contents[deedCounter] or "Deed Record" in contents[
                        deedCounter]):
                        # print(deed)
                        information["DRRecords"].append(deed)
                        break
                    deedCounter += 1



            # end of property extraction
            if ("Boats" in contents[propertyCounter]):
                break
            propertyCounter += 1


        # print(information)

        # input personal data based on dates
        addresses = information["PropertyAddress"].keys()

        info_data = []
        for i in information.values():
            if type(i) == dict:
                break
            info_data.append(i)

        with open(csv_file_name, 'a') as f:
            writer = csv.writer(f)
            # write the header
            for address in addresses:
                writer.writerow(info_data + [address] + [information["PropertyAddress"][address]])
        f.close()


        # with open(csv_file_name, 'w') as f:
        #     writer = csv.writer(f)
        #
        #     # write the header
        #     writer.writerow(csv_columns)
        #
        # f.close()

# In[30]:


# In[31]:



AR_columns = ["ARAddress", "ARCounty", "ARRecordingDate", "ARSaleDate", "ARSalePrice", "ARAssessedValue",
              "ARMarketLandValue", "ARMarketImprovementValue", "ARTotalMarketValue"]
DR_columns = ["DRAddress", "DRContractDate", "DRRecordingDate", "DRLoanAmount", "DRLoanType", "DRTitleCompany",
              "DRTransactionType", "DRDescription", "DRLenderInformation"]
all_columns = csv_columns + AR_columns + DR_columns

masterList = []

# for addyDict in results:
#     mergeThis = {}
#     for ARDict in completeARList:
#         tempRatio = fuzz.ratio(ARDict["ARAddress"].lower().strip(), addyDict["PropertyAddress"].lower().strip())
#         if tempRatio > 90:
#             addyDict = {**addyDict, **ARDict}
#
#     for DRDict in completeDRList:
#         holdingRatio = fuzz.ratio(DRDict["DRAddress"].lower().strip(), addyDict["PropertyAddress"].lower().strip())
#         if holdingRatio > 90:
#             addyDict = {**addyDict, **DRDict}
#
#     masterList.append(addyDict)

# csv_file = "2_13_Moody.csv"
# masterList = sorted(masterList, key=lambda x: x['FirstName'])
#
# try:
#     with open(csv_file, 'w', newline="") as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=all_columns)
#         writer.writeheader()
#         for data in masterList:
#             writer.writerow(data)
# except IOError:
#     print("IOError")

# In[ ]:


# In[ ]:




