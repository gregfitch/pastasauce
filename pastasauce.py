# x
# x
# x

# import json
import requests


class PastaSauce(object):
    """"""
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
        self.user = Account(sauce_username, sauce_access_key)
        self.request = SauceComm(self.user)

    def get_user(self):
        return self.user.username

    def get_access_key(self):
        return self.user.access_key

    def get_headers(self):
        return self.request.headers


class Account(object):
    """"""

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """"""
        self.username = sauce_username
        self.access_key = sauce_access_key


class SauceComm(object):
    """"""
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'

    def __init__(self, user_account):
        """"""
        if type(user_account) is not Account:
            raise TypeError('Expected %s, received %s' %
                            (type(Account), type(user_account)))
        self.request = requests.Response()
        self.user = user_account
        self.headers = {}

    def get_auth_pair(self):
        """"""
        return (self.user.username, self.user.access_key)

    def request(self, method, url_append, extra_data=None):
        """"""
        full_url = 'https://saucelabs.com/rest/v1/%s' % url_append
        return full_url
