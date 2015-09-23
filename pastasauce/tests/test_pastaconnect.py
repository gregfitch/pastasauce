from pastasauce.pastasauce import Account, PastaConnect
import pytest


INCOMPLETE = True


def test_pastaconnect_initialization():
    ''''''
    pc = PastaConnect(Account())
    assert(type(pc) is PastaConnect)
    assert(type(pc.user) is Account)


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastaconnect_links():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastaconnect_get_sauce_connect_links():
    ''''''
