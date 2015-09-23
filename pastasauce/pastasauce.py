# x
# x
# x

import os
import datetime
import re
import requests
from sys import modules
from requests import Session
from urllib import parse
from bs4 import BeautifulSoup

__version__ = '0.1.1'


class PastaDecorator(object):
    """
    This decorator is required to iterate over browser
    dictionary setups with pytest
    """
    @classmethod
    def on_platforms(cls, platforms):
        def decorator(base_class):
            module = modules[base_class.__module__].__dict__
            for i, platform in enumerate(platforms):
                d = dict(base_class.__dict__)
                d['desired_capabilities'] = platform
                name = "%s_%s" % (base_class.__name__, i + 1)
                module[name] = type(name, (base_class,), d)
        return decorator


class PastaSauce(object):
    """
    Sauce Labs access object for use by Python 3
    """
    # obj HTTP communication strings
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    OPTIONS = 'OPTIONS'
    # access command options
    ALL = 'all'
    APPIUM = 'appium'
    WEBDRIVER = 'webdriver'
    SELENIUM = 'selenium-rc'
    # sub-account levels
    FREE = 'free'
    SMALL = 'small'
    TEAM = 'team'
    COM = 'com'
    COM_PLUS = 'complus'
    # test types
    QUNIT = 'qunit'
    JASMINE = 'jasmine'
    YUI = 'YUI Test'
    MOCHA = 'mocha'
    CUSTOM = 'custom'

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """
        Build a user account from (in order):
        1. passed values
        2. envrionment variables 'SAUCE_USERNAME' and
           'SAUCE_ACCESS_KEY'
        3. NoneType (only unauthenticated commands
           available to blank auth)
        """
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

    def get_headers(self):
        """"""
        return self.comm.get_headers()

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

    def get_user_info(self):
        """"""
        url = 'users/%s' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_user_activity(self):
        """"""
        url = 'users/%s/activity' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_account_usage(self, username=None, start=None, end=None):
        """"""
        user = username if bool(username) else self.comm.user
        url = 'users/%s/usage%s' % \
            (user, PastaHelper.get_date_encode_string(start, end))
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def create_sub_account(self, username, password, name, email, plan=None):
        """"""
        url = 'users/%s' % self.user.username
        data = {}
        data['username'] = username
        data['password'] = password
        data['name'] = name
        data['email'] = email
        if plan is not None:
            data['plan'] = plan
        return self.comm.send_request(PastaSauce.POST, url, data)

    def update_subaccount_plan(self, username, plan):
        """"""
        url = '%s/subscription' % username
        data = {'plan': plan, }
        return self.comm.send_request(PastaSauce.POST, url, data)

    def delete_subaccount_plan(self, username):
        """"""
        url = '%s/subscription' % username
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def get_user_concurrency(self):
        """"""
        url = 'users/%s/concurrency' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_jobs(self, username=None, number_of_jobs=100, get_full_data=False,
                 skip_jobs=0, jobs_from=None, jobs_to=None, output=None):
        """"""
        user = username if username is not None else self.user.username
        url_args = {}
        if number_of_jobs != 100 and number_of_jobs > 0:
            url_args['limit'] = number_of_jobs
        if get_full_data:
            url_args['full'] = get_full_data
        if skip_jobs > 0:
            url_args['skip_jobs'] = skip_jobs
        if jobs_from is not None:
            url_args['from'] = jobs_from
        if jobs_to is not None:
            url_args['to'] = jobs_to
        if output is not None:
            url_args['format'] = output
        url = '%s/jobs%s' % \
            (user, PastaHelper.get_jobs_encode_string(url_args))
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_full_job_info(self, job_id):
        """"""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def update_job(self, job_id, name=None, tags=None, public=None,
                   passed=None, build=None, custom_data=None):
        """"""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = {}
        if name is not None:
            data['name'] = name
        if tags is not None:
            data['tags'] = tags
        if public is not None:
            data['public'] = public
        if passed is not None:
            data['passed'] = passed
        if build is not None:
            data['build'] = build
        if custom_data is not None:
            data['custom_data'] = custom_data
        if data == {}:
            data = None
        return self.comm.send_request(PastaSauce.PUT, url, data)

    def delete_job(self, job_id):
        """"""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def stop_job(self, job_id):
        """"""
        url = '%s/jobs/%s/stop' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.PUT, url, data)

    def get_job_asset_filenames(self, job_id):
        """"""
        url = '%s/jobs/%s/assets' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_job_asset_file(self, job_id, file_name):
        """"""
        url = '%s/jobs/%s/assets/%s' % (self.user.username, job_id, file_name)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def delete_job_asset_files(self, job_id):
        """"""
        url = '%s/jobs/%s/assets' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def upload_file(self, file_name, file_type, file_path=None,
                    overwrite=False):
        """"""
        if file_path is None:
            file_path = '.'
        if file_path.endswith('/'):
            file_path = file_path[:-1]
        if not os.path.isfile('%s/%s' % (file_path, file_name)):
            raise Exception.OSError.FileNotFoundError(
                '%s/%s not found' % (file_path, file_name))
        url = 'storage/%s/%s%s' % (self.user.username,
                                   file_name,
                                   '?overwrite=true' if overwrite else '')
        data = None
        file_data = {'file': open('%s/%s' % (file_path, file_name), 'rb')}
        return self.comm.send_request(PastaSauce.POST, url, data, file_data)

    def get_storage_file_names(self):
        """"""
        url = 'storage/%s' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_tunnel_ids(self, username=None):
        """"""
        user = username if username is not None else self.user.username
        url = '%s/tunnels' % user
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_tunnel_info(self, tunnel_id):
        """"""
        url = '%s/tunnels/%s' % (self.user.username, tunnel_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def delete_tunnel(self, tunnel_id):
        """"""
        url = '%s/tunnels/%s' % (self.user.username, tunnel_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def start_js_unit_tests(self, platforms, test_url, framework,
                            tunnel_id=None, parent=None, test_max=None):
        """"""
        url = '%s/js-tests' % self.user.username
        data = {}
        data['platforms'] = platforms
        data['url'] = test_url
        data['framework'] = framework
        if tunnel_id is not None:
            data['tunnelIdentifier'] = tunnel_id
        elif parent is not None:
            data['parentTunnel'] = parent
        if test_max is not None:
            data['maxDuration'] = test_max
        return self.comm.send_request(PastaSauce.POST, url, data)

    def get_unit_test_status(self, test_ids):
        """"""
        url = '%s/js-tests/status' % self.user.username
        data = {}
        data['js tests'] = test_ids
        return self.comm.send_request(PastaSauce.POST, url, data)

    def get_bug_types(self):
        """"""
        url = 'bugs/types'
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_bug_fields(self, bug_id):
        """"""
        url = 'bugs/types/%s' % bug_id
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_bug_details(self, bug_id):
        """"""
        url = 'bugs/detail/%s' % bug_id
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def update_bug(self, bug_id, title=None, description=None):
        """"""
        url = 'bugs/update/%s' % bug_id
        data = {}
        if title is not None:
            data['Title'] = title
        if description is not None:
            data['Description'] = description
        return self.comm.send_request(PastaSauce.PUT, url, data)


class PastaHelper(object):
    """
    Internal helper functions for PastaSauce
    Not intended for public use
    """

    def date_type_base_valid(self, date):
        """"""
        if type(date) is not datetime.date and type(date) is not str:
            return False
        return True

    def str_date_split(self, date_str):
        """"""
        split = date_str.split('-')
        if len(split) != 3:
            raise ValueError('str date must be "YYYY-MM-DD"')
        try:
            s_year = int(split[0])
            s_month = int(split[1])
            s_day = int(split[2])
            return datetime.date(s_year, s_month, s_day)
        except Exception:
            raise ValueError('str date must be "YYYY-MM-DD"')

    def check_dates(self, start, end):
        """"""
        if start is None and end is None:
            return (None, None)
        begin_set = None
        end_set = None
        if bool(start):
            self.date_type_base_valid(start)
            begin_set = self. \
                str_date_split(start) if type(start) is str else start
            if datetime.date.today() < begin_set:
                begin_set = datetime.date.today()
        if bool(end):
            self.date_type_base_valid(end)
            end_set = self. \
                str_date_split(end) if type(end) is str else end
        if bool(begin_set) and bool(end_set):
            return (begin_set, end_set) if begin_set < end_set else \
                   (end_set, begin_set)
        if bool(begin_set):
            return (begin_set, datetime.date.today())
        return (datetime.date.min, end_set)

    def get_date_encode_string(self, start, end):
        """"""
        url_data = {}
        start_date, end_date = self.check_dates(start, end)
        if bool(start_date):
            url_data['start'] = start_date.isoformat()
        if bool(end_date):
            url_data['end'] = end_date.isoformat()
        return ('?' + parse.urlencode(url_data)) if url_data != {} else ''

    def get_jobs_encode_string(self, url_data):
        """"""
        return ('?' + parse.urlencode(url_data)) if url_data != {} else ''

    def get_job_visibility_options(self):
        """"""
        return {'Public': {'public', 'public restricted', 'share', 'true'},
                'Private': {'team', 'false', 'private'}, }

    def get_unit_frameworks(self):
        """"""
        return ['qunit', 'jasmine', 'YUI Test', 'mocha', 'custom']


class Account(object):
    """
    Basic access account object for Sauce Labs
    """

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """
        Setup an account with a user and access key or an
        empty call for unauthenticated requests
        """
        if sauce_username is None or sauce_access_key is None:
            self.username = None
            self.access_key = None
        else:
            self.username = '%s' % sauce_username
            self.access_key = '%s' % sauce_access_key

    def set_username(self, user):
        """
        Change the username.

        :: Return True if successful
        :: Clear user and access key information if passed
           None and return False
        """
        if user is None:
            self.username = None
            self.access_key = None
            return False
        self.username = '%s' % user
        return True

    def set_access_key(self, access_key):
        """
        Change the user access_key.

        :: Return True if successful
        :: Clear user and access key information if passed
           None and return False
        """
        if access_key is None:
            self.username = None
            self.access_key = None
            return False
        self.access_key = '%s' % access_key
        return True


class SauceComm(object):
    """
    Setup and control PastaSauce communication to Sauce
    Labs.

    For unauthenticated commands, can setup with empty user
    SauceComm(Account())
    """
    # HTTP request options
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    OPTIONS = 'OPTIONS'

    def __init__(self, user_account):
        """
        Setup the SauceComm object including the personal
        lambda dictionary of HTTP request methods.

        Raise a TypeError if SauceComm is not given a
        PastaSauce Account.
        """
        if type(user_account) is not Account:
            raise TypeError('Expected %s, received %s' %
                            (Account, type(user_account)))
        self.user = user_account
        self.request = Session()
        # set user authentication; if an empty user is sent assume the requesst
        # does not require auth
        if self.user.username is not None and self.user.access_key is not None:
            self.request.auth = (self.user.username, self.user.access_key)
        self.request.headers.update({'Content-Type': 'application/json'})
        # no switch statement in Python; use lambda dict instead
        self.methods = {
            SauceComm.DELETE: (lambda url, data:
                               self.request.delete(url=url, json=data)),
            SauceComm.GET: (lambda url, data:
                            self.request.get(url=url, json=data)),
            SauceComm.HEAD: (lambda url, data:
                             self.request.head(url=url, json=data)),
            SauceComm.PATCH: (lambda url, data:
                              self.request.delete(url=url, json=data)),
            SauceComm.POST: (lambda url, data, files=None:
                             self.request.post(url=url, json=data, files=files)
                             ),
            SauceComm.PUT: (lambda url, data:
                            self.request.put(url=url, json=data)),
            SauceComm.OPTIONS: (lambda url, data:
                                self.request.options(url=url, json=data)),
        }

    def send_request(self, method, url_append, extra_data=None, files=None):
        """
        Send the request object with data package and any
        supplemental files to Sauce Labs.

        Raise an InvalidProtocol exception if 'method' is
        not in the class method list.
        """
        if method not in self.methods:
            raise InvalidProtocol('Unknown protocol "%s"' % method)
        full_url = 'https://saucelabs.com/rest/v1/%s' % url_append
        if files is not None:
            return self.methods[SauceComm.POST](full_url, extra_data, files)
        return self.methods[method](full_url, extra_data)

    def get_protocols(self):
        """
        Return a sorted list of available protocols
        """
        protocols = []
        for method in self.methods.keys():
            protocols.append(method)
        return protocols.sort()

    def get_headers(self):
        """
        Return request object headers
        """
        return self.request.headers


class PastaConnect(object):
    """ Incomplete
    Manage SauceConnect

    To Do:
    a) setup a tunnel
    b) manage tunnels
    c) tear down session tunnels when finished
    """

    def __init__(self, user_account):
        """"""
        self.user = user_account

    def get_sauce_connect_links(self):
        """ Incomplete
        Return SauceConnect URL links
        """
        r = requests.get('https://docs.saucelabs.com/reference/sauce-connect')
        soup = BeautifulSoup(r.text)
        return self.links(soup.body)

    def links(self, blob):
        """ Incomplete
        Parse blob looking for GZ, ZIP, DMG and EXE links

        :: Return [] if no file links are located
        :: Return a list of links after successfully
           parsing the blob
        """
        links = []
        regex = re.compile('''\"https:\/\/s[a-zA-Z\./\-]*[\d\.]{5,}
                           [a-zA-Z\./\-0-9]*[(gz|zip|dmg|exe)]\"''',
                           re.VERBOSE)
        pattern = regex.findall(blob)
        if pattern is None:
            return links
        for match in pattern:
            if match[1:-1] not in links:
                links.append(match[1:-1])
        return links


class InvalidProtocol(Exception):
    """
    Raised when an unknown protocol is attempted during a
    request submission
    """
    def __init__(self, message='', *args):
        self.message = message
        super(self).__init__(message, *args)
