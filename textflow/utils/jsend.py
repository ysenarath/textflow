def response(status, **kwargs):
    reply = {'status': status, }
    for k, v in kwargs.items():
        reply[k] = v
    return reply


def success(data=None):
    if data is None:
        data = {}
    return response('success', data=data)


def fail(data=None):
    if data is None:
        data = {}
    return response('fail', data=data)


def error(message='Unable to determine error. Please contact admin for fixing this issue.'):
    return response('error', message=message)
