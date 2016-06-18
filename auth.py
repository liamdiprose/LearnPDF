"""
Module used to autheticate the user into Learn

Learn Login Process:
1. Send user credidentals and hidden values in login form
2. Server responds with SAML authentication tokens
3. Post tokens to SAML
4. Cookie is made, which can be used to browse and download stuff from Learn
"""
import requests
from bs4 import BeautifulSoup
import logging
import json
from time import time

# Specify how long a cookie stays fresh (seconds)
COOKIE_TIMEOUT = 5000


class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message


def get_hidden_vars(response):
    """Get hidden values from form for post"""
    logging.debug("Obtaining Learn Page Hidden Parameters")
    soup = BeautifulSoup(response.text, 'html.parser')
    form_action = "https://learn.canterbury.ac.nz/Shibboleth.sso/Login"
    form = soup.find('form', action=form_action).find_all('input', 'hidden')
    return {val.get('name'): val.get('value') for val in form}


def announce_session(session, parameters):
    login_url = "https://learn.canterbury.ac.nz/Shibboleth.sso/Login"
    r = session.get(login_url, params=parameters)


def send_credentials(session, username, password):
    """Initial sending of credidentials"""
    logging.debug("Sending learn credidentals")
    payload = {'j_username': username, 'j_password': password}
    auth_url = "https://login.canterbury.ac.nz/idp/Authn/UserPassword"

    response = BeautifulSoup(session.post(auth_url, data=payload).text, 'html.parser')
    if response.find('form').get('action') == 'https://learn.canterbury.ac.nz/Shibboleth.sso/SAML2/POST':
        return str(response)
    else:
        raise AuthenticationError("Your login credidentals were incorrect")


def parse_SAML(html):
    """Scrape data from SAML response"""
    logging.debug("Parsing SAML authenitication")
    soup = BeautifulSoup(html, 'html.parser')
    saml_state = soup.find('input', attrs={'name': 'RelayState'})
    saml_response = soup.find('input', attrs={'name': 'SAMLResponse'})
    return {'RelayState': saml_state.get('value'),
            'SAMLResponse': saml_response.get('value')}


def auth_saml(session, saml_values):
    """Get SAML stuff for the session"""
    logging.debug("Authenticating with SAML")
    saml_url = "https://learn.canterbury.ac.nz/Shibboleth.sso/SAML2/POST"
    session.post(saml_url, data=saml_values)


def get_new_authenticated_session(username, password):
    """
    Returns an authenticated requests.session() for learn
    :param username: String Username
    :param password: String Password
    :return: Authenticated Requests session
    """
    if not username:
        username = input("Learn Username: ")
    if not password:
        import getpass
        password = getpass.getpass()
    session = requests.session()
    session.cookies.clear()
    login_url = "https://learn.canterbury.ac.nz/login/index.php"

    session.get(login_url)
    hidden_vars = {'target': 'https://learn.canterbury.ac.nz/auth/shibboleth/index.php',
             'entityID': 'https://idp.canterbury.ac.nz/idp/shibboleth'}
    announce_session(session, hidden_vars)
    saml = send_credentials(session, username, password)
    samlvars = parse_SAML(saml)
    auth_saml(session, samlvars)
    session_to_file(session)
    return session


def session_to_file(session):
    """Save a session to file"""
    with open('learn.cookies', 'w') as f:
        logging.debug("Cookies saved to file")
        cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
        json.dump([int(time()), cookie_dict], f)


def session_from_file():
    """Load a session from file"""
    with open('learn.cookies', 'r') as f:
        cookie_dict = json.load(f)[1]
        cookies = requests.utils.cookiejar_from_dict(cookie_dict)
    session = requests.session()
    session.cookies = cookies
    return session


def get_authenticated_session(username, password):
    """
    Try use a fresh cookie if availble, otherwise login with username and password
    :param username: String
    :param password: String
    :return: Authenticated Requests session
    """
    try:
        with open('learn.cookies', 'r') as f:
            if json.load(f)[0] + COOKIE_TIMEOUT > time():
                logging.debug("Fresh cookie was found")
                return session_from_file()
            else:
                logging.debug("Stale cookie found, reauthenticating")
                return get_new_authenticated_session(username, password)
    except FileNotFoundError:
        logging.debug("No cookie file found")
        return get_new_authenticated_session(username, password)

if __name__ == '__main__':
    import getpass
    logging.basicConfig(level=logging.DEBUG)
    learn_url = "https://learn.canterbury.ac.nz/"

    session = get_authenticated_session(username=None, password=None)
    r = session.get(learn_url).text
    soup = BeautifulSoup(r, 'html.parser')
    if soup.find('span', attrs={'class': 'login'}):
        raise ConnectionError("Could not log in. This error should not happen, the error should be caught upstream")
    else:
        print("You have successfully logged in")
