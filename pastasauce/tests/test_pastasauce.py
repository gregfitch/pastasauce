import os
from pastasauce.pastasauce import PastaSauce, Account, SauceComm
import random
import string
import requests
import json
import pytest
import datetime

INCOMPLETE = True
no_user_account = True if os.environ['SAUCE_USERNAME'] is None else False


class PastaTestHelper(object):
    """
    helper functions for test cases
    """
    @classmethod
    def random_string(cls, length):
        """
        get a random string of ASCII letters and number of length
        """
        return ''.join([random.choice(string.ascii_letters +
                       string.digits) for n in range(length)])


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
    assert(failed_test.text == 'Not Found')


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
    platform['name'] = 'PastaSauce_unittest_action' + \
                       datetime.today().isoformat()
    driver = webdriver.Remote(
        command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' %
        (user.get_user(), user.get_access_key()),
        desired_capabilities=platform)
    driver.implicitly_wait(10)


@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_user_activity():
    import datetime
    ps = PastaSauce()
    user_activity = ps.get_user_activity()
    assert(type(user_activity) is requests.models.Response)
    assert(user_activity.status_code == requests.codes.ok)
    activity_data = json.loads(user_activity.text)
    assert(type(activity_data) is dict)
    assert('jobs' in activity_data)
    assert(activity_data['datestamp'][-1] == datetime.today().isoformat())
    desired_cap = {
        'platform': "Mac OS X 10.9",
        'browserName': "chrome",
        'version': "31",
    }
    run_saucelabs_test_action(desired_cap, ps)
    time.sleep(1)
    user_activity = ps.get_user_activity()
    assert(user_activity[ps.get_user]['in progress'] >= 1)  # test running


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


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_create_sub_account():
    ps = PastaSauce()
    ps.create_sub_account()


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_update_subaccount_plan():
    ps = PastaSauce()
    ps.update_subaccount_plan()


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_delete_subaccount_plan():
    ps = PastaSauce()
    ps.delete_subaccount_plan()


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_pastasauce_get_user_concurrency():
    ps = PastaSauce()
    print(ps)


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
