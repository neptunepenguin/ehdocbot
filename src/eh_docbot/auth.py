#!/usr/bin/env python

import os, sys, time, re, logging, getopt
from itertools import dropwhile
import requests
from bs4 import BeautifulSoup


__doc__ = """
"""
log = logging.getLogger(__name__)  # don't reuse this name, seriously, don't
EH_USERNAME = None
EH_PASSWORD = None
WIKI_USERNAME = None
WIKI_PASSWORD = None
# It is polite to wait a moment between several requests to the same
# webserver, this function exists to ensure that we can change the wait time
# depending on whether we are testing things (and running a handful of
# requests) or working with hundreds or thousands of requests.
# We sleep different times for GET and for POST because most webservers have
# different counters for those, and consider POST much more dangerous.
GET_SLEEP = 0.3
POST_SLEEP = 3
SUMMARY = 'Automated Tag Group Fixes'
HEADERS = { 'User-Agent' :
    'Mozilla/5.0 (X11; Linux; rv:13) Gecko/20100101 Firefox/54.0' }
EH_LOGIN_DATA = {
    'UserName' : None,
    'PassWord' : None,
    'x'        : 0,
    'y'        : 0
}
WIKI_LOGIN_DATA = {
    'wpName'         : None,
    'wpPassword'     : None,
    'wploginattempt' : 'Log in',
    'wpEditToken'    : None,
    'authAction'     : 'login',
    'title'          : 'Special:UserLogin',
    'force'          : None,
    'wpLoginToken'   : None
}


def auth_forums(session):
    '''
    Performs the login procedure to the EH forums,
    this is needed for us to be able to retrieve the lists of tag groups.
    '''
    url = 'https://forums.e-hentai.org'
    log.info('GET %s', url)
    r = session.get(url, headers=HEADERS)
    log.debug('HTTP %d', r.status_code)
    session_cookie = session.cookies.get('ipb_session_id')
    soup = BeautifulSoup(r.content, 'html.parser')
    form = soup.find('form')  # login is the first form
    log.info( 'FORUM login with user %s, password ******, session %s',
              EH_USERNAME, session_cookie )
    time.sleep(GET_SLEEP)
    url = form.attrs.get('action')
    log.info('POST %s', url)
    rp = session.post(url, data=EH_LOGIN_DATA, headers=HEADERS)
    log.debug('HTTP %d', rp.status_code)
    if not rp.ok:
        raise RuntimeError("Can't continue without FORUM auth")
    log.info( 'FORUM login DONE with user %s, password ******, cookies %s',
              EH_USERNAME, session.cookies )
    return session


def auth_wiki(session):
    '''
    Performs the login procedure to the EH wiki.
    We need the credentials to the wiki to update (POST)
    the revised tag templates.
    '''
    url = ('https://ehwiki.org/index.php'
           '?title=Special:UserLogin&returnto=Main+Page')
    r = session.get(url, headers=HEADERS)
    session_cookie = session.cookies.get('ehwiki_session')
    soup = BeautifulSoup(r.content, 'html.parser')
    edit_input = soup.select('input[name="wpEditToken"]')[0]
    token_input = soup.select('input[name="wpLoginToken"]')[0]
    edit_token = edit_input.attrs.get('value')
    login_token = token_input.attrs.get('value')
    WIKI_LOGIN_DATA['wpEditToken'] = edit_token
    WIKI_LOGIN_DATA['wpLoginToken'] = login_token
    log.info( 'WIKI login: user %s, password ***, session %s, tokens %s|%s',
              WIKI_USERNAME, session_cookie, edit_token, login_token )
    time.sleep(GET_SLEEP)
    log.info('POST %s', url)
    rp = session.post(url, data=WIKI_LOGIN_DATA, headers=HEADERS)
    log.debug('HTTP %d', rp.status_code)
    if not rp.ok:
        raise RuntimeError("Can't continue without WIKI auth")
    log.info( 'WIKI login DONE with: %s', session.cookies)
    return session

