from pastasauce.pastasauce import Account
import pytest


INCOMPLETE = True


def test_account_initialization():
    a = Account()
    assert(type(a) == Account)
    assert(a.username is None)
    assert(a.access_key is None)
    a = Account('name')
    assert(a.username is None)
    assert(a.access_key is None)
    a = Account(sauce_username='name')
    assert(a.username is None)
    assert(a.access_key is None)
    a = Account(sauce_access_key='key')
    assert(a.username is None)
    assert(a.access_key is None)
    a = Account(sauce_access_key=None)
    assert(a.username is None)
    assert(a.access_key is None)
    a = Account('name', 'key')
    assert(a.username == 'name')
    assert(a.access_key == 'key')
    a = Account(sauce_username='name', sauce_access_key='key')
    assert(a.username == 'name')
    assert(a.access_key == 'key')


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_account_set_username():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_account_set_access_key():
    ''''''
