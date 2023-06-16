import os, sys

root = "Merged Analyst Documents - Lexis Nexis + LinkedIn/SP Analyst PDFs"
for entry in os.scandir(root):
    name = entry.name
    pdf = name[-4:]
    if pdf != ".pdf":
    # if name[-1] == "_":
        new_name = name + ".pdf"
        os.rename(entry, "Merged Analyst Documents - Lexis Nexis + LinkedIn/SP Analyst PDFs/" + new_name)