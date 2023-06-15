#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, sys, subprocess
import tempfile
import re
import csv


# initialize CSV file

csv_file = "Moodys" + "CriminalReports.csv"
criminal_columns = ["PDFName", "CaseFilingDate", "OffenseDate", "Categories", "CaseType", "CourtOffense", "CourtDisposition"]

with open(csv_file, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(criminal_columns)
f.close()

# begin conversion
PDFTOTEXT_PATH = '/usr/local/bin/pdftotext'
for fileName in os.scandir('Merged Analyst Documents - Lexis Nexis + LinkedIn/Moodys Analyst PDFs'):
    if fileName.is_file() and fileName.name.endswith(".pdf"):
        information = {"PDFName": None, "CriminalRecords" : []}
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
        for line in encodedlineArray:
            contents.append(line.decode("Latin1"))

        # voter registration extraction below
        lineCounter = 0
        while lineCounter < len(contents):
            if "Court Report" in contents[lineCounter]:
                reportInfo = {"CaseFilingDate" : None, "OffenseDate" : None, "Categories" : None, "CaseType" : None, "CourtOffense" : None, "CourtDisposition" : None}
                i = lineCounter + 1
                while i < len(contents):
                    if ("Case Filing Date" in contents[i]):
                        reportInfo["CaseFilingDate"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Offense Date" in contents[i]):
                        reportInfo["OffenseDate"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Categories" in contents[i]):
                        reportInfo["Categories"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Case Type" in contents[i]):
                        reportInfo["CaseType"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Court Offense" in contents[i]):
                        reportInfo["CourtOffense"] = contents[i][contents[i].find(":") + 1:].strip()
                    if ("Court Disposition" in contents[i] and "Date" not in contents[i]):
                        reportInfo["CourtDisposition"] = contents[i][contents[i].find(":") + 1:].strip()

                    if "Court Report" in contents[i]:
                        break
                    if "Cellular & Alternate Phones" in contents[i]:
                        break

                    i += 1
                # print(reportInfo)
                information["CriminalRecords"].append(reportInfo)

            lineCounter += 1

        # print(information)
        # input criminal info based on name
        criminalrecords = information["CriminalRecords"]
        for record in criminalrecords:
            data = []
            for value in record.values():
                data.append(value)
            with open(csv_file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([information["PDFName"]] + data)
            f.close()
