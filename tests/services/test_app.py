""" Test App """

from textflow import TextFlow


def test_create_app_no_config():
    """ Create and test app object

    :return: None
    """
    tf = None
    try:
        tf = TextFlow(None)
    except AttributeError:
        pass
    assert tf is None
