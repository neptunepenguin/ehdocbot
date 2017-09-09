#!/usr/bin/env python

import os, sys, time, re, logging, getopt
from itertools import dropwhile
import requests
from bs4 import BeautifulSoup


__doc__ = """
"""
log = logging.getLogger(__name__)


class DeepDict(object):
    '''
    A dictionary of dictionaries that updates the keys of the deep dictionaries
    instead of its own keys.  In other words it more-or-less works as a
    dictionary but has a special update method.
    '''
    def __init__(self, *args, **kwargs):
        '''Keep the actual dictionary internally.'''
        self._dict = dict(*args, **kwargs)

    def __getattr__(self, key):
        '''
        Will raise the correct exception for a dictionary.  Note that
        retrieving `._dict` still works, not sure why.
        '''
        return self._dict[key]
    __getitem__ = __getattr__

    def __setattr__(self, key, value):
        '''
        Makes an exception for items starting with underscores, this is needed
        to actually maintain the internal dictionary without falling into and
        infinite loop during `self._dict`.
        '''
        if key.startswith('_'):
            super(DeepDict, self).__setattr__(key, value)
        else:
            self._dict[key] = value

    def __setitem__(self, key, value):
        '''Just pass to the dictionary, do not need to use __setattr__.'''
        self._dict[key] = value

    def __delattr__(self, key):
        '''Allow for deletion. As attributes and as keys.'''
        del self._dict[key]
    __delitem__ = __delattr__

    def __iter__(self):
        '''Required to be able to go through the keys in a for loop.'''
        for k in self._dict:
            yield k

    def items(self):
        '''
        `.items` is used in python 3.x, `.iteritems` is for backward
        compatibility with python 2.x.
        '''
        for k,v in self._dict.items():
            yield k,v
    iteritems = items

    def keys(self):
        '''Just pass the keys of the internal dict, hide `._dict`.'''
        return self._dict.keys()

    def update(self, deep_dict):
        '''
        Perform a deep update: if both the value in the current internal
        dictionary and the value in the item being placed over it are some kind
        of dictionary (i.e. have the `update` attribute, remember duck typing)
        then join them together instead of replaying one with another.
        '''
        for k,v in deep_dict.items():
            deep = self._dict.get(k)
            if deep and hasattr(deep, 'update') and hasattr(v, 'update'):
                deep.update(v)
            else:
                self._dict[k] = v

    def __str__(self):
        '''
        String representation similar to a dictionary.  Keep the `__repr__`
        the same, to print nicely inside other dictionaries.
        '''
        return 'deep%s' % self._dict
    __repr__ = __str__


class ReSession(requests.Session):
    '''
    Some spam detectors will simply drop your connection, without any
    explanation.  That's fine, we simply reconnect after waiting for a
    reasonable amount of time.  We use the same sleep time for POST and for
    the methods in the session because it should be a sensible amount of time.
    If you are getting a log of warnings from the re-connecting sessions you
    need to increase the wait.
    '''
    def get(self, *args, **kwargs):
        '''
        The GET handler, recursively calls itself after a while if it fails on
        the first try.  There is no limit on the number of tries because if the
        connection problem is persistent we need to manually investigate.
        '''
        try:
            return super(ReconnectingSession, self).get(*args, **kwargs)
        except requests.exceptions.ConnectionError as ex:
            log.warn('Recovering from: %s', ex)
            time.sleep(POST_SLEEP)
            return self.get(*args, *kwargs)

    def post(self, *args, **kwargs):
        '''
        Handler for POST requests.  Just like the GET handler above, calls
        itself after a while if the connection went bust.
        '''
        try:
            return super(ReconnectingSession, self).post(*args, **kwargs)
        except requests.exceptions.ConnectionError as ex:
            log.warn('Recovering from: %s', ex)
            time.sleep(POST_SLEEP)
            return self.post(*args, *kwargs)


def build_post_data(dictionary, soup, *args):
    '''
    A trivial POST data builder: searches for the correct input in a beautiful
    soup parsed web page and updates the dictionary to be sent by `requests`.
    This works well when there is a single `<form>` on a page but may fail if
    there is more than one.

    NOTE: the dictionary is passed by reference so it is modified directly.
    '''
    for field in args:
        input = soup.select('input[name="%s"]' % field)
        if input:
            token = input[0].attrs.get('value')
            log.debug('POST Found %s => %s', field, token)
            dictionary[field] = token
        else:
            log.debug('POST NOT Found %s', field)
            dictionary[field] = None


def log_extra(change_p, code, tag, female=None, male=None, misc=None):
    '''
    A default format to print to standard output, i.e. this is the only place
    where print() is used.  This format allows us to grep the generated log for
    records that were updated (:True:200:), records that do not exist on the
    wiki (:False:404:), records that are already in the correct format and need
    not be updated (:False:200:), and records which failed to be updated
    (anything else).
    '''
    format = 'CHANGE:%s:%s:%s:female:%s,male:%s,misc:%s'
    print( format % (change_p, code, tag, female, male, misc) )

