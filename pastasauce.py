# x
# x
# x

# import json
import os
from requests import Response, Session


class PastaSauce(object):
    """"""
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    OPTIONS = 'OPTIONS'
    ALL = 'all'
    APPIUM = 'appium'
    WEBDRIVER = 'webdriver'
    SELENIUM = 'selenium-rc'
    FREE = 'free'
    SMALL = 'small'
    TEAM = 'team'
    COM = 'com'
    COM_PLUS = 'complus'

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """"""
        if sauce_username is None:
            sauce_username = os.environ.get('SAUCE_USERNAME')
        if sauce_access_key is None:
            sauce_access_key = os.environ.get('SAUCE_ACCESS_KEY')
        self.user = Account(sauce_username, sauce_access_key)
        self.comm = SauceComm(self.user)

    def get_user(self):
        """"""
        return self.user.username

    def get_access_key(self):
        """"""
        return self.user.access_key

    def get_sauce_labs_status(self):
        """"""
        url = 'info/status'
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_supported_platforms(self, api):
        """"""
        url = 'info/platforms/%s' % api
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_bug_types(self):
        """"""
        url = 'bugs/types'
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_user_info(self):
        """"""
        url = 'users/%s' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)


class Account(object):
    """"""

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """"""
        if sauce_username is None or sauce_access_key is None:
            self.username = None
            self.access_key = None
        else:
            self.username = '%s' % sauce_username
            self.access_key = '%s' % sauce_access_key

    def set_username(self, user):
        """"""
        if user is None:
            self.username = None
            self.access_key = None
            return False
        self.username = '%s' % user
        return True

    def set_access_key(self, access_key):
        """"""
        if access_key is None:
            self.username = None
            self.access_key = None
            return False
        self.access_key = '%s' % access_key
        return True


class SauceComm(object):
    """"""
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    OPTIONS = 'OPTIONS'

    def __init__(self, user_account):
        """"""
        if type(user_account) is not Account:
            raise TypeError('Expected %s, received %s' %
                            (type(Account), type(user_account)))
        self.user = user_account
        self.request = Session()
        self.response = Response()
        if self.user.username is not None and self.user.access_key is not None:
            self.request.auth = (self.user.username, self.user.access_key)
        self.request.headers.update({'Content-Type': 'application/json'})
        self.methods = {
            SauceComm.DELETE: (
                lambda x, y: self.request.delete(url=x, data=y)),
            SauceComm.GET: (
                lambda x, y: self.request.get(url=x, data=y)),
            SauceComm.HEAD: (
                lambda x, y: self.request.head(url=x, data=y)),
            SauceComm.PATCH: (
                lambda x, y: self.request.delete(url=x, data=y)),
            SauceComm.POST: (
                lambda x, y: self.request.post(url=x, data=y)),
            SauceComm.PUT: (
                lambda x, y: self.request.put(url=x, data=y)),
            SauceComm.OPTIONS: (
                lambda x, y: self.request.options(url=x, data=y)), }

    def send_request(self, method, url_append, extra_data=None):
        """"""
        if method not in self.methods:
            raise InvalidProtocol('Unknown protocol "%s"' % method)
        full_url = 'https://saucelabs.com/rest/v1/%s' % url_append
        self.response = self.methods[method](full_url, extra_data)
        return self.response


class InvalidProtocol(Exception):
    """"""
    def __init__(self, *args):
        """"""
        self.args = args

    def __str__(self):
        """"""
        return str(self.args[0] if len(self.args) <= 1 else self.args)

    def __repr__(self):
        """"""
        func_args = repr(self.args) if self.args else "()"
        return self.__class__.__name__ + func_args
