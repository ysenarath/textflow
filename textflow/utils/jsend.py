""" JSend Response formatting """


def response(status, **kwargs):
    """ Generic response format

    :param status: status content
    :param kwargs: other content
    :return: dictionary with status and other
    """
    reply = {'status': status, }
    for k, v in kwargs.items():
        reply[k] = v
    return reply


def success(data=None):
    """ Json formatting for success message

    :param data: data field
    :return: Json Response
    """
    if data is None:
        data = {}
    return response('success', data=data)


def fail(data=None):
    """ Json formatting for failed message

    :param data: data field
    :return: Json Response
    """
    if data is None:
        data = {}
    return response('fail', data=data)


def error(message='Unable to determine error. Please contact admin for fixing this issue.'):
    """ Json formatting for error message

    :param message: message field
    :return: Json Response
    """
    return response('error', message=message)
