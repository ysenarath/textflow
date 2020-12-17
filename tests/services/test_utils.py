""" Test Utils - Dictionary Object """

from textflow.utils import Dictionary as Map


def test_dictionary_arg():
    """ Test dict arg in init dict

    :return: None
    """
    sample = Map({'foo': 'bar'}, bar='foo')
    assert sample.foo == 'bar'


def test_dictionary_kwarg():
    """ Test dict kwarg in init dict

    :return: None
    """
    sample = Map({'foo': 'bar'}, bar='foo')
    assert sample.bar == 'foo'
