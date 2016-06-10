"""
API Wrapper for the learn website
"""
import requests
from auth import get_authenticated_session
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlsplit

import re
import os

import logging

learn_url = "https://learn.canterbury.ac.nz/"


class Course(object):
    def __init__(self, shortname, link, id, longname):
        self.id = id
        self.shortname = shortname
        self.link = link
        self.longname = longname

    def __str__(self):
        return self.shortname + " (" + self.id + ")"

    @classmethod
    def factory(self, a_tag):
        link = a_tag.get('href')
        id = parse_qs(urlsplit(link)[3])['id'][0]
        shorttitle = a_tag.get('title')
        longtitle = a_tag.text
        c = Course(shorttitle, link, id, longtitle)
        return id, c


class Section(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __str__(self):
        return self.name + " (" + self.id + ")"

class PDFFile(object):
    def __init__(self, name, learn_id):
        self.name = name
        self.id = learn_id

    def download(self, session, filename):
        download_url = learn_url + "/mod/resource/view.php"

        page = session.get(download_url, params={'id': self.id})
        soup = BeautifulSoup(page.text, 'html.parser')
        pdf_area = soup.find('section', id="region-main")

        if not pdf_area:
            logging.debug("Link didnt find expected website structure, probally not a PDF link")
            return # Function is void, just return null and skip file

        pdf_link = pdf_area.find('object').get('data')

        print("\t\t " + self.name)


        try:
            os.makedirs(os.path.dirname(filename))
        except FileExistsError:
            pass

        with open(filename, 'wb') as f:
            r = session.get(pdf_link)
            f.write(r.content)

        # with open(filename, 'wb') as f:
        #     r = session.get(pdf_link, stream=True, params={'forcedownload': '1'})
        #     for chunk in page.iter_content(chunk_size=1024):
        #         if chunk: # filter out keep-alive new chunks
        #             f.write(chunk)


def login(username=None, password=None):
    return get_authenticated_session(username, password)


def get_courses(session):
    """
    Returns dictionary of courses from learn page
    :param session: Autheticated requests object
    :return: List of courses (as objects)
    """
    soup = BeautifulSoup(session.get(learn_url).text, 'html.parser')
    courseblock = soup.find('div', attrs={'data-block': 'course_list'})
    courses = {}
    for course in courseblock.find_all('li'):   #TODO: This can be made into a dictonary comprehension
        id, c_obj = Course.factory(course.a)
        courses[id] = c_obj

    return courses


def get_sections(session, course):
    """
    Returns dictionary of sections of a given course
    :param session:
    :param course: Course Object
    :return: Dictionary of sections of given course
    """
    r = session.get(course.link)
    #text = re.sub(u"&amp;", "NOTHING", r.text)
    #print(text)
    soup = BeautifulSoup(r.text, 'html.parser')
    sectionblock = soup.find('div', attrs={'data-block': 'menu_site_and_course'})
    #print(sectionblock.prettify())
    sections = sectionblock.find_all('ul')[1].find_all('li')

    section_list = []

    for section in sections:
        #print(section.a.get('title'))
        link = section.a.get('href')
        #print(link)
        # id = parse_qs(urlsplit(section.a.get('href'))[3])
        id = re.search("(?<=ion\=)([0-9]+)", urlsplit(link)[3])
        section_list.append(Section(section.text, id.group(1)))
        #print("id", id.group(0))  # TODO; ampersand & is escaped, but is still evaluated
    return section_list


def make_url(course_id, section_id):
    """http://learn.canterbury.ac.nz/course/view.php?id=1536&section=1"""
    return learn_url + "/course/view.php"

def get_pdfs(session, course_id, section_id=None):
    r = session.get(learn_url + "/course/view.php", params={'id': course_id, 'section': section_id})
    soup = BeautifulSoup(r.text, 'html.parser')

    title = soup.find("h3", {'class': 'sectionname'})
    #print("TITLE: " + title.text)

    main_container = soup.find("section", {'id': 'region-main'})

    if not main_container:
        #print("No class:course-content")
        return

    pdf_id = []
    for link in main_container.findAll("a"):
        url = link.get('href')
        if not url: continue
        #print("Testing: " + url, end=' ')
        t = re.search(r".*/mod/resource/view.php\?id=([0-9]+)", url) # TODO better var name

        if t:
            id = t.group(1)
            name = link.text


            pdf_id.append(PDFFile(name, id))

    return pdf_id


