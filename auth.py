"""
Module used to autheticate the user into learn
"""
import requests
from bs4 import BeautifulSoup
import logging
import json
from time import time

COOKIE_TIMEOUT = 5000

class AutheticationError(Exception):
    def __init__(self, message):
        self.message = message

def get_hidden_vars(response):
    logging.debug("Obtaining Learn Page Hidden Parameters")
    soup = BeautifulSoup(response.text, 'html.parser')
    form_action = "https://learn.canterbury.ac.nz/Shibboleth.sso/Login"
    form = soup.find('form', action=form_action).find_all('input', 'hidden')
    return {val.get('name'): val.get('value') for val in form}

def annouce_session(session, parameters):
    login_url = "https://learn.canterbury.ac.nz/Shibboleth.sso/Login"
    r = session.get(login_url, params=parameters)

def send_credentials(session, username, password):
    logging.info("Sending learn credidentals")
    payload = {'j_username': username, 'j_password': password}
    auth_url = "https://login.canterbury.ac.nz/idp/Authn/UserPassword"

    response = BeautifulSoup(session.post(auth_url, data=payload).text, 'html.parser')
    if response.find('form').get('action') == 'https://learn.canterbury.ac.nz/Shibboleth.sso/SAML2/POST':
        return str(response)
    else:
        raise AutheticationError("Your login credidentals were incorrect")

def parse_SAML(html):
    logging.debug("Parsing SAML authenitication")
    soup = BeautifulSoup(html, 'html.parser')
    saml_state = soup.find('input', attrs={'name': 'RelayState'})
    saml_response = soup.find('input', attrs={'name': 'SAMLResponse'})
    return {'RelayState': saml_state.get('value'),
            'SAMLResponse': saml_response.get('value')}

def auth_saml(session, saml_values):
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
    hvars = {'target': 'https://learn.canterbury.ac.nz/auth/shibboleth/index.php',
             'entityID': 'https://idp.canterbury.ac.nz/idp/shibboleth'}
    annouce_session(session, hvars)
    saml = send_credentials(session, username, password)
    samlvars = parse_SAML(saml)
    auth_saml(session, samlvars)
    session_to_file(session)
    return session

def session_to_file(session):
    with open('learn.cookies', 'w') as f:
        logging.info("Cookies saved to file")
        cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
        json.dump([int(time()), cookie_dict], f)

def session_from_file():
    with open('learn.cookies', 'r') as f:
        cookie_dict = json.load(f)[1]
        cookies = requests.utils.cookiejar_from_dict(cookie_dict)
    session = requests.session()
    session.cookies = cookies
    return session

    # TODO: Find method of finding if cookies are still fresh

def get_authenticated_session(username, password):
    try:
        with open('learn.cookies', 'r') as f:
            if json.load(f)[0] + COOKIE_TIMEOUT > time():
                logging.info("Fresh cookie was found")
                return session_from_file()
            else:
                logging.info("Stale cookie found, reauthenticating")
                return get_new_authenticated_session(username, password)
    except FileNotFoundError:
        logging.info("No cookie file found")
        return get_new_authenticated_session(username, password)

if __name__ == '__main__':
    import getpass
    logging.basicConfig(level=logging.INFO)
    learn_url = "https://learn.canterbury.ac.nz/"

    session = get_authenticated_session(username=None, password=None)
    r = session.get(learn_url).text
    soup = BeautifulSoup(r, 'html.parser')
    if soup.find('span', attrs={'class': 'login'}):
        raise ConnectionError("Could not log in. This error should not happen, the error should be caught upstream")
    else:
        print("You have successfully logged in")
