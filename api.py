import requests
import urllib.parse as urlparse

class Learn(object):

    TOKEN_URL = "http://learn.canterbury.ac.nz/login/token.php?username={username}&password={password}&service=moodle_mobile_app"
    WWW_ROOT = "http://learn.canterbury.ac.nz/webservice/rest/server.php"

    def __init__(self, username=None, password=None, token=None):
        if token:
            self.token = token  # TODO : Check token if invalid
        else:
            self.token = Learn.get_token(username, password)

        self.userid = self.get_userid()


    @staticmethod
    def get_token(username, password):

        r = requests.post(Learn.TOKEN_URL.format(username=username, password=password)).json()

        if "error" in r:
            raise PermissionError(r['error'])
        elif "token" in r:
            return r['token']
        else:
            raise NotImplementedError(r)

    def make_request(self, function, **kwargs):
        params = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json"
        }
        params.update(kwargs)

        return requests.get(Learn.WWW_ROOT, params=params).json()


    def get_userid(self):
        return self.make_request("core_webservice_get_site_info")['userid']


    def get_course_list(self):
        return self.make_request("core_enrol_get_users_courses", userid=self.userid)

    def all_files(self):
        for course in self.get_course_list():
            for file in self.get_course_files(course['id']):
                file['course_name'] = course['shortname']
                yield file

    def get_course_files(self, courseid):
        """ Sorry """
        sections = self.make_request("core_course_get_contents", courseid=courseid)

        for section in sections:
            if section["name"] != "Section":
                for module in section["modules"]:
                    if "contents" in module:
                        for content in module["contents"]:
                            if content["type"] == "file":
                                yield {
                                    "url": inject_param(content["fileurl"], token=self.token),
                                    "section_name": section["name"],
                                    "name": module["name"],
                                    "filename": content["filename"],
                                    "filesize": content["filesize"],
                                    "timemodified": content["timemodified"]
                                }

def inject_param(url, **kwargs):
    url_parts = list(urlparse.urlparse(url))

    query = dict(urlparse.parse_qsl(url_parts[4]))

    query.update(kwargs)
    url_parts[4] = urlparse.urlencode(query)

    return urlparse.urlunparse(url_parts)
