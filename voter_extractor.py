#!/usr/bin/env python
# coding: utf-8


import os, sys, subprocess
import tempfile
import re
import csv

csv_file = "SP" + "VoterRegitstration.csv"
voting_columns = ["PDFName", "RegistrationDate", "PartyAffiliation", "ActiveStatus", "LastVoteDate"]

with open(csv_file, 'w') as f:
    writer = csv.writer(f)

    writer.writerow(voting_columns)

f.close()

# begin conversion
PDFTOTEXT_PATH = '/usr/local/bin/pdftotext'
for fileName in os.scandir('Merged Analyst Documents - Lexis Nexis + LinkedIn/SP Analyst PDFs'):
    if fileName.is_file() and fileName.name.endswith(".pdf"):
        information = {"PDFName": None, "VotingRecords" : []}
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

        # for manually checking texts and extraction
        # new_name = fileName.name[:-4]
        #
        # with open('txts/' + new_name + '.txt', 'w') as f:
        #     f.write(str(pdfTextLayout, 'UTF-8'))
        # f.close()


        # decoding both from bytes to string- might need some modifications bc of latin1 decoding
        contents = []
        tableFile = []
        for line in encodedlineArray:
            contents.append(line.decode("Latin1"))

        # voter registration extraction below
        # 3/26/23 Note- you need to add if-statements below to extract the other information Professor Lock wants you to do
        lineCounter = 0
        while lineCounter < len(contents):
            if ":" in contents[lineCounter] and "Voter Registration" in contents[lineCounter]:
                reportInfo = {"RegistrationDate" : None, "PartyAffiliation" : None, "ActiveStatus" : None, "LastVoteDate" : None}
                i = lineCounter + 1
                while i < len(contents):
                    if ("Registration Date" in contents[i]):
                        reportInfo["RegistrationDate"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Last Vote Date" in contents[i]):
                        reportInfo["LastVoteDate"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Party Affiliation" in contents[i]):
                        reportInfo["PartyAffiliation"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Active Status" in contents[i]):
                        reportInfo["ActiveStatus"] = contents[i][contents[i].find(":") + 1:].strip()

                    if ":" in contents[i] and "Voter Registration" in contents[i]:
                        break
                    if "Professional Licenses" in contents[i]:
                        break

                    i += 1
                information["VotingRecords"].append(reportInfo)

            lineCounter += 1
        # print(information)
        # input voting info based on name
        votingrecords = information["VotingRecords"]
        for record in votingrecords:
            data = []
            for value in record.values():
                data.append(value)
            with open(csv_file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([information["PDFName"]] + data)
            f.close()

# In[ ]:




