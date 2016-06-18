from learnapi import *
import os
import logging
import time
# logging.basicConfig(level=logging.INFO)

s = login()

for course in get_courses(s).values():
    print("Course: " + str(course))
    for section in get_sections(s, course):
        print("Section: " + str(section))
        for pdf_file in get_pdfs(s, course.id, section.id):
            filename = "{root_dir}/{course}/{section}/{pdf_name}".format(
                root_dir="learn/",
                course=course.shortname,
                section=section.name,
                pdf_name=pdf_file.name
            )

            pdf_file.download(s, filename)
            time.sleep(1)

print("Finished Successfully")
