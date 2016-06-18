"""
API Wrapper for the learn website
"""
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
        return self.shortname #+ " (" + self.id + ")"

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
        return self.name #+ " (" + self.id + ")"


class LearnFile(object):
    def __init__(self, name, learn_id):
        self.name = name
        self.id = learn_id

    def download(self, session, filename):
        """Save online Learn resource to file"""
        download_url = learn_url + "/mod/resource/view.php"

        page = session.get(download_url, params={'id': self.id})
        soup = BeautifulSoup(page.text, 'html.parser')


        pdf_area = soup.find('section', id="region-main")

        title = soup.find('title')
        title = title.text if title else "<Not found>"
        if not pdf_area:
            # HTML was not found, meaning, the file was already downloaded
            logging.debug("Link didnt find expected website structure on page \"" + title  + "\", (probally not PDF)")
            r = page # Page went striaght to the file, not the the final website
            pdf_link = download_url + "&id=" + str(self.id)
        else:
            pdf_link = pdf_area.find('object').get('data')
            if not pdf_link:
                return
            logging.debug("Starting download for: " + pdf_link)
            r = session.get(pdf_link)

        file_ext = urlsplit(r.url).path.split(".")[-1]

        # Uncomment this if you want to filter the file extention
        # if file_ext.lower() != "pdf": return

        if not file_ext: file_ext = ''

        try:
            os.makedirs(os.path.dirname(filename))
        except FileExistsError:
            pass

        print("[{}] {}".format(file_ext.upper(), self.name))
        with open(filename + "." + file_ext, 'wb') as f:


            data = r.content

            if not data:
                logging.error("Data was empty")

            f.write(data)

            #
            # while True:
            #     data = r.read(1024)
            #     if not data:
            #         break
            #     f.write(data)
            # for i, chunk in enumerate(r.iter_content(chunk_size=1024)):
            #     print("Downloading: {} bits".format(i*1024), end="\r")
            #     f.write(chunk)


def login(username=None, password=None):
    """
    Login to learn with username and password.
    :return Requests session object
        """
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
    for course in courseblock.find_all('li'):  # TODO: This can be made into a dictonary comprehension
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
    soup = BeautifulSoup(r.text, 'html.parser')
    sectionblock = soup.find('div', attrs={'data-block': 'menu_site_and_course'})
    sections = sectionblock.find_all('ul')[1].find_all('li')

    section_list = []

    for section in sections:
        link = section.a.get('href')

        id = re.search("(?<=ion\=)([0-9]+)", urlsplit(link)[3])
        section_list.append(Section(section.text, id.group(1)))
        # TODO; ampersand & is escaped, but is still evaluated
    return section_list


def get_pdfs(session, course_id, section_id=None):
    """
    Scrape all files listed on a page (Doesnt currently filter pdf links)
    :param session: Requests Session Object
    :param course_id: Integer
    :param section_id: Integer
    :return: List of PDF files (learn resource ID's)
    """
    r = session.get(learn_url + "/course/view.php", params={'id': course_id, 'section': section_id})
    soup = BeautifulSoup(r.text, 'html.parser')


    main_container = soup.find("section", {'id': 'region-main'})

    if not main_container:
        # print("No class:course-content")
        return

    pdf_id = []
    for link in main_container.findAll("a"):
        url = link.get('href')
        if not url: continue
        # print("Testing: " + url, end=' ')
        t = re.search(r".*/mod/resource/view.php\?id=([0-9]+)", url)  # TODO better var name

        if t:
            id = t.group(1)

            # TODO: This appends " File" to filename for some reason
            name = re.search("(.*) File", link.text)
            if not name: name = link.text

            pdf_id.append(LearnFile(name.group(1), id))

    return pdf_id
