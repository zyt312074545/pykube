from pykube import is_null, is_number, str2list


def test_is_null():
    error = is_null('')
    assert error is False
    right = is_null('right')
    assert right is True


def test_is_number():
    error = is_number('e')
    assert error is False
    right = is_number('1994')
    assert right is True


def test_str2list():
    string = 'a    b  c '
    result = str2list(string)
    assert result == ['a', 'b', 'c']
