from pastasauce.pastasauce import PastaHelper
import pytest


INCOMPLETE = True


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_date_type_base_valid():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_str_date_split():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_check_dates():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_get_date_encode_string():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_get_jobs_encode_string():
    ''''''


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastahelper_get_job_visibility_options():
    ''''''


def test_pastahelper_get_unit_frameworks():
    ''''''
    ph = PastaHelper()
    framework_list = ph.get_unit_frameworks()
    assert(type(framework_list) is list)
    assert('custom' in framework_list)
