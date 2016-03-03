import os
from pastasauce.pastasauce import PastaSauce, Account, SauceComm
import requests
import json
import pytest

INCOMPLETE = True
no_user_account = True if os.environ['SAUCE_USERNAME'] is None else False
test_user = {}


class PastaTestHelper(object):
    """
    helper functions for test cases
    """
    @classmethod
    def random_string(cls, length):
        """
        get a random string of ASCII letters and number of length
        """
        import random
        import string
        return ''.join([random.choice(string.ascii_letters +
                       string.digits) for n in range(length)])

    @classmethod
    def build_test_user(cls):
        from bs4 import BeautifulSoup
        req = requests.get('http://www.behindthename.com/random/random.php?' +
                           'number=1&gender=both&surname=&randomsurname=yes' +
                           '&all=no&usage_eng=1')
        soup = BeautifulSoup(req.content, 'html.parser')
        name = ''
        for tag in soup.find_all('a', class_='plain'):
            name += ' ' + tag.string
        name = name[1:]
        test_user['username'] = 'ost' + PastaTestHelper.random_string(10)
        test_user['password'] = PastaTestHelper.random_string(15)
        test_user['fullname'] = name
        test_user['emailadr'] = test_user['username'] + '@openstax.org'
        return test_user


def test_pastasauce_initialization():
    ps = PastaSauce()
    assert(type(ps) == PastaSauce)
    assert(type(ps.user) == Account)
    assert(type(ps.comm) == SauceComm)


def test_pastasauce_get_user():
    environ_username = os.environ['SAUCE_USERNAME']
    if environ_username is not None:
        del os.environ['SAUCE_USERNAME']
    ps = PastaSauce(None, None)
    assert(ps.get_user() is None)
    os.environ['SAUCE_USERNAME'] = environ_username
    ps = PastaSauce(os.environ.get('SAUCE_USERNAME'), '')
    assert(ps.get_user() == os.environ.get('SAUCE_USERNAME'))
    random_username = PastaTestHelper.random_string(15)
    ps = PastaSauce(random_username, '')
    assert(ps.get_user() == random_username)


def test_pastasauce_get_access_key():
    environ_access_key = os.environ['SAUCE_ACCESS_KEY']
    if environ_access_key is not None:
        del os.environ['SAUCE_ACCESS_KEY']
    ps = PastaSauce(None, None)
    assert(ps.get_access_key() is None)
    os.environ['SAUCE_ACCESS_KEY'] = environ_access_key
    ps = PastaSauce('', os.environ.get('SAUCE_ACCESS_KEY'))
    assert(ps.get_access_key() == os.environ.get('SAUCE_ACCESS_KEY'))
    random_access_key = PastaTestHelper.random_string(15)
    ps = PastaSauce('', random_access_key)
    assert(ps.get_access_key() == random_access_key)


def test_pastasauce_get_headers():
    ps = PastaSauce()
    headers = ps.get_headers()
    assert(type(headers) == requests.structures.CaseInsensitiveDict)
    assert('Content-Type' in headers)
    assert(headers['Content-Type'] == 'application/json')


def test_pastasauce_get_sauce_labs_status():
    ps = PastaSauce()
    status = ps.get_sauce_labs_status()
    assert(type(status) is requests.models.Response)
    assert(status.status_code == requests.codes.ok)
    assert('status_message' in json.loads(status.text))


def test_pastasauce_get_supported_platforms():
    ps = PastaSauce()
    all_available = ps.get_supported_platforms('all')
    assert(type(all_available) is requests.models.Response)
    assert(all_available.status_code == requests.codes.ok)
    assert(type(json.loads(all_available.text)) is list)
    appium = ps.get_supported_platforms('appium')
    assert(type(appium) is requests.models.Response)
    assert(appium.status_code == requests.codes.ok)
    assert(type(json.loads(appium.text)) is list)
    webdriver = ps.get_supported_platforms('webdriver')
    assert(type(webdriver) is requests.models.Response)
    assert(webdriver.status_code == requests.codes.ok)
    assert(type(json.loads(webdriver.text)) is list)
    failed_test = ps.get_supported_platforms('does_not_exist')
    assert(type(failed_test) is requests.models.Response)
    assert(failed_test.status_code != requests.codes.ok)
    assert(not failed_test.ok)


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_user_info():
    ps = PastaSauce()
    user_info = ps.get_user_info()
    assert(type(user_info) is requests.models.Response)
    assert(user_info.status_code == requests.codes.ok)
    assert(type(json.loads(user_info.text)) is dict)
    assert('id' in json.loads(user_info.text))
    assert(json.loads(user_info.text)['id'] == ps.get_user())


def run_saucelabs_test_action(platform, user):
    from selenium import webdriver
    from datetime import datetime
    platform['name'] = 'PastaSauce_unittest_action' + \
                       datetime.today().isoformat()
    driver = webdriver.Remote(
        command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
        (user.get_user(), user.get_access_key()),
        desired_capabilities=platform)
    driver.implicitly_wait(10)
    driver.get("https://tutor-qa.openstax.org")
    login = driver.find_element_by_link_text('Login')
    login.click()


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_current_job_activity():
    # import datetime
    import time
    from multiprocessing import Process
    ps = PastaSauce()
    user_activity = ps.get_current_job_activity()
    assert(type(user_activity) is requests.models.Response)
    assert(user_activity.status_code == requests.codes.ok)
    activity_data = json.loads(user_activity.text)
    assert(type(activity_data) is dict)
    assert('subaccounts' in activity_data)
    # assert(activity_data['datestamp'][-1] ==
    #        datetime.date.today().isoformat())
    desired_cap = {
        'platform': "Mac OS X 10.9",
        'browserName': "chrome",
        'version': "31",
    }
    proc = Process(target=run_saucelabs_test_action,
                   args=(desired_cap, ps))
    proc.start()
    # run_saucelabs_test_action(desired_cap, ps)
    time.sleep(3)
    user_activity = ps.get_current_job_activity()
    # with a test running check activity
    activities = json.loads(user_activity.text)
    assert('subaccounts' in activities)
    activity = activities['subaccounts']
    assert(ps.get_user() in activity)
    user = activity[ps.get_user()]
    assert(user['in progress'] >= 1)
    proc.join()


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_user_activity():
    """"""


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_account_usage():
    ps = PastaSauce()
    account_usage = ps.get_account_usage()
    assert(type(account_usage) is requests.models.Response)
    assert(account_usage.status_code == requests.codes.ok)
    usage_data = json.loads(account_usage.text)
    assert(type(usage_data) is dict)
    assert('usage' in usage_data)
    assert(usage_data['username'] == ps.get_user())


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_create_sub_account():
    user = PastaTestHelper.build_test_user()
    ps = PastaSauce()
    account = ps.create_sub_account(username=user['username'],
                                    password=user['password'],
                                    name=user['fullname'],
                                    email=user['emailadr'])
    assert(type(account) is requests.models.Response)
    if account.status_code != requests.codes.created:
        assert(account.status_code == requests.codes.bad_request)
        assert(account.json()['errors'] == 'Subaccount capacity exhausted.')
        return
    account_data = json.loads(account.text)
    assert(type(account_data) is dict)
    assert('first_name' in account_data)
    assert(account_data['parent'] == ps.get_user())
    assert(account_data['name'] == user['fullname'])


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
@pytest.mark.skipif(test_user == {}, reason='Subaccount not initialized')
def test_pastasauce_update_subaccount_plan():
    ps = PastaSauce()
    new_plan = ps.update_subaccount_plan(test_user['username'], 'free')
    assert(type(new_plan) is requests.models.Response)
    assert(new_plan.status_code == requests.codes.ok)
    new_plan_data = json.loads(new_plan.text)
    assert(type(new_plan_data) is dict)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
@pytest.mark.skipif(test_user == {}, reason='Subaccount not initialized')
def test_pastasauce_delete_subaccount_plan():
    ps = PastaSauce()
    removed = ps.delete_subaccount_plan(test_user['username'])
    assert(type(removed) is requests.models.Response)
    removed_data = json.loads(removed.text)
    if removed.status_code != requests.codes.ok:
        assert('message' in removed_data)


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_user_concurrency():
    ps = PastaSauce()
    concurrent = ps.get_user_concurrency()
    assert(type(concurrent) is requests.models.Response)
    assert(concurrent.status_code == requests.codes.ok)
    concurrent_data = json.loads(concurrent.text)
    assert(type(concurrent_data) is dict)
    assert('concurrency' in concurrent_data)
    assert(ps.get_user() in concurrent_data['concurrency'])
    user = concurrent_data['concurrency'][ps.get_user()]
    remaining = user['remaining']['overall']
    current = user['current']['overall']
    limit = json.loads(ps.get_user_info().text)
    limit = limit['concurrency_limit']['overall']
    assert((remaining + current) == limit)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_jobs():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_full_job_info():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_update_job():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_delete_job():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_stop_job():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_job_asset_filenames():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_job_asset_files():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_upload_file():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_storage_file_names():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_tunnel_info():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_delete_tunnel():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_start_js_unit_tests():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_unit_test_status():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastasauce_get_bug_types():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastasauce_get_bug_fields():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_bug_details():
    ps = PastaSauce()
    print(ps)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_update_bug():
    ps = PastaSauce()
    print(ps)
