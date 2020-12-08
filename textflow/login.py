""" Login related functions """

from urllib.parse import urlparse, urljoin

from flask import request
from flask_login import LoginManager

login_manager = LoginManager()


def is_safe_url(target):
    """ Checks whether URL target is safe.

    :param target: URL
    :return: whether target is safe or not
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
