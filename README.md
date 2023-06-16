# LexisNexis PDF Information Extractor

Derived from information extractor from Evan Yang's module. Original: https://github.com/evanyang22/March_LexisNexis_Program-Checkpoint

# Guide through each folder and file

- evan files — directory of Evan's programs that create the foundation of the new ones in the repository
- old — drafts of possible information extractor files. one uses a different pdf to text module called pymupdf while the other attempted to use different methods to extract the necessary information. renamer.py is a filler python file used to rename a bulk of the S&P files because the naming scheme was a bit off
- criminal_extractor.py — extracting criminal records for each person if there are any. Output is a csv file with each row corresponding to an analyst and a criminal record that was discovered in the pdf
- dataset_cleaner.py — matching the names of the analysts on an Excel sheet to the folder of pdfs. Output is a csv file with the analyst name, corresponding pdf, and corresponding name match score with the fuzzwuzz module in columns
- pdftotext_info_scraper.py — basically the bulk of the extractor, extracts personal information and address records, as well as AR and DR information. Output are three csv files; one with the analyst's information iterated by the individual address records/date range, one with analysts' AR records, and one with analysts' DR records
- voter_extractor.py — extracting voting records for each person if there are any. Output is a csv file with each row corresponding to an analyst and a voting record that was discovered in the pdf

# List of important information that you should be familiar with before continuing this project. 

**Background information- What should you be familiar with before you start?**
1. Python coding and following modules
os module: https://docs.python.org/3/library/os.html
-  used to interact with the operating system and run command line codes frequently, along with importing and reading files
pandas library: https://www.w3schools.com/python/pandas/default.asp
-  used to store and collect data, along with some analysis and cleaning

2. CSV files- a lot of information is going to be stored using csv files, so get familiar with using Python to write to them and modify them
https://www.businessinsider.com/guides/tech/what-is-csv-file 
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html

3. pdftotext - pdftotext itself was downloaded, and its path and subprocess was used to operate and extract pdf to text
https://www.xpdfreader.com/pdftotext-man.html

**Set Up- How to set up and run these programs?**
1. Download and install pdftotext at https://www.xpdfreader.com/pdftotext-man.html
2. Download the programs and put them into a folder that contains all the Lexis Nexus reports in PDF version. 
3. Run the program using a commandline
Ex: python _____.py 

An output csv file should pop up in the folder when it is done. You can look at the output to see how well it performed. 


If you have any questions, feel free to reach out to me at ellie.paek@emory.edu.
