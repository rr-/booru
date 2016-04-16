import pytest
from szurubooru import errors
from szurubooru.util import misc
from datetime import datetime

dt = datetime

def test_parsing_empty_date_time():
    with pytest.raises(errors.ValidationError):
        misc.parse_time_range('')

@pytest.mark.parametrize('input,output', [
    ('today',       (dt(1997, 1, 2, 0, 0, 0), dt(1997, 1, 2, 23, 59, 59))),
    ('yesterday',   (dt(1997, 1, 1, 0, 0, 0), dt(1997, 1, 1, 23, 59, 59))),
    ('1999',        (dt(1999, 1, 1, 0, 0, 0), dt(1999, 12, 31, 23, 59, 59))),
    ('1999-2',      (dt(1999, 2, 1, 0, 0, 0), dt(1999, 2, 28, 23, 59, 59))),
    ('1999-02',     (dt(1999, 2, 1, 0, 0, 0), dt(1999, 2, 28, 23, 59, 59))),
    ('1999-2-6',    (dt(1999, 2, 6, 0, 0, 0), dt(1999, 2, 6, 23, 59, 59))),
    ('1999-02-6',   (dt(1999, 2, 6, 0, 0, 0), dt(1999, 2, 6, 23, 59, 59))),
    ('1999-2-06',   (dt(1999, 2, 6, 0, 0, 0), dt(1999, 2, 6, 23, 59, 59))),
    ('1999-02-06',  (dt(1999, 2, 6, 0, 0, 0), dt(1999, 2, 6, 23, 59, 59))),
])
def test_parsing_date_time(fake_datetime, input, output):
    fake_datetime(datetime(1997, 1, 2, 3, 4, 5))
    assert misc.parse_time_range(input) == output

@pytest.mark.parametrize('input,output', [
    ([], []),
    (['a', 'b', 'c'], ['a', 'b', 'c']),
    (['a', 'b', 'a'], ['a', 'b']),
    (['a', 'a', 'b'], ['a', 'b']),
    (['a', 'A', 'b'], ['a', 'b']),
    (['a', 'A', 'b', 'B'], ['a', 'b']),
])
def test_icase_unique(input, output):
    assert misc.icase_unique(input) == output
