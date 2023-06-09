#!/usr/bin/env python
# coding: utf-8

# In[29]:


import os, sys, subprocess
import pdftotext
import re

def organize_name(disorganized_name):
    """
    makes the name into a nicer, more organizable name
    :param disorganized_name: string of disorganized name
    :return: tuple/triple of first name, last name, middle name
    """
    first = ""
    middle = None
    last = disorganized_name.split(",")[0]
    first = disorganized_name.split()[1]
    if len(disorganized_name.split()) == 3:
        middle = disorganized_name.split()[2]
    return (first, last, middle)


PDFTOTEXT_PATH = '/usr/local/bin/pdftotext'
files = [f for f in os.listdir('../pdfs') if not f.startswith('.')]
for file in files:
    information = {"PDFName": file,
                   "FullName": None, "FirstName": None, "LastName": None,
                   "County": None,
                   "PhoneNumber": None,
                   "SSN": None,
                   "DOBMonth": None, "DOBYear": None,
                   "Gender": None,
                   "LexID": None,
                   "Email1": None, "Email2": None, "Email3": None, "Email4": None, "Email5": None,
                   "Email6": None,
                   "CurrentAddress": None, "PropertyAddress": None, "DateRange": None}

    try:
        q = subprocess.Popen([PDFTOTEXT_PATH, '-f', '2', '-layout', 'pdfs/' + file, "-"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pdfTextLayout, err = q.communicate()
        # print(err)
    except:
        print('pdftotext Layout failed')
    # getting -table version and storign as pdfTextTable
    # try:
    #     q = subprocess.Popen([PDFTOTEXT_PATH, '-table', file, "-"], stdout=subprocess.PIPE,
    #                          stderr=subprocess.PIPE)
    #     pdfTextTable, err = q.communicate()
    # except:
    #     print('pdftotext Table failed')
    # reading and extracting
    new_name = file[:-4]

    with open('txts/' + new_name + '.txt', 'w') as f:
        f.write(str(pdfTextLayout, 'UTF-8'))
    f.close()


    with open('txts/' + new_name + '.txt', 'r') as f:
        contents = f.readlines()
        # for content in contents:
        #     content.strip()

        # print(contents[100])
        # gender extraction

        r = re.compile('Female\n')
        gender = list(filter(r.match, contents))
        print(gender)
        if "Gender: Female" in contents:
            information["Gender"] = "Female"
        else:
            information["Gender"] = "Male"
        # for i in contents:
        #     print(i)
        #     print("Woof")

        # # name extraction
        # index = contents.index("Phone\n") + 1
        # information["FullName"] = contents[index][:-1]
        # organized_name = organize_name(contents[index])
        # information["FirstName"] = organized_name[0]
        # information["LastName"] = organized_name[1]
        #
        # # current address extraction (?)
        # current_address = ""
        # index += 1
        # current_address += contents[index][:-1] + ", "
        # index += 1
        # current_address += contents[index][:-1]
        # information["CurrentAddress"] = current_address
        #
        # # county extraction
        # index += 2
        # information["County"] = contents[index][:-1]

        # SSN extraction
        # r = re.compile("SSN:")
        # ssn = list(filter(r.match, contents))
        # if (len(ssn)) != 0:
        #     information["SSN"] = ssn[0][5:-1]

        # DOB extraction
        # r = re.compile("[0-9]/[0-9][0-9]")
        # dob = list(filter(r.match, contents))[0][:-1]
        # dob = dob.split("/")
        # information["DOBMonth"] = dob[0]
        # information["DOBYear"] = dob[1]

        # LexID extraction
        # r = re.compile("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")
        # lexid = list(filter(r.match, contents))[0][:-1]
        # information["LexID"] = lexid
        #
        # # email extraction
        # r = re.compile("^.+@.+\.[A-Z]{2,3}$")
        # emails = list(filter(r.match, contents))
        # if (len(emails)) != 0:
        #     for i in range(len(emails)):
        #         information["Email" + str(i + 1)] = emails[i][:-1]

        # print(contents)

    f.close()
    # print(information)