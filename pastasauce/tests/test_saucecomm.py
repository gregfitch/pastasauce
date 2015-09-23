from pastasauce.pastasauce import Account, SauceComm, InvalidProtocol
import pytest
import os


INCOMPLETE = True
no_user_account = True if os.environ['SAUCE_USERNAME'] is None else False


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_saucecomm_initialization():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_saucecomm_send_request():
    ''''''
    raise InvalidProtocol()


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_saucecomm_get_protocols():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
@pytest.mark.skipif(no_user_account, reason='Need a SauceLabs account')
def test_saucecomm_get_headers():
    ''''''
    sc = SauceComm(Account())
    headers = sc.get_headers()
    assert(type(headers) is dict)
