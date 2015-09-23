from pastasauce.pastasauce import PastaDecorator
import pytest


INCOMPLETE = True


@pytest.mark.skipif(INCOMPLETE, reason='Incomplete')
def test_pastasauce_decorator_on_platforms(capsys):
    ''''''
    platforms = [{
        'platform': 'Windows 10',
        'browserName': 'internet explorer',
        'version': '11'
    }, {
        'platform': 'Windows 10',
        'browserName': 'internet explorer',
        'version': '10',
    }]
    pd = PastaDecorator()
    pd.on_platforms(platforms)
    print('PastaDecorator: ' + str(pd))
    assert(False)
