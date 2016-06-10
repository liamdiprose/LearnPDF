
from learnapi import *
import os
import logging

logging.basicConfig(level=logging.INFO)


s = login()
filepath = "learn/"
print("logged in")

for course in get_courses(s).values():
    print(course)
    for section in get_sections(s, course):
        print("\t" + str(section))
        for pdf_file in get_pdfs(s, course.id, section.id):

            filename = filepath + course.shortname + "/" + section.name + "/" + pdf_file.name + ".pdf"

            pdf_file.download(s, filename)
