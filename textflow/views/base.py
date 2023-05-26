"""Base view for textflow."""
import collections

from flask import (
    current_app,
    request as flask_request,
    render_template_string,
    render_template as flask_render_template,
    redirect, url_for
)

__all__ = [
    'render_template',
    'Pagination',
]


def render_template(path, **kwargs) -> str:
    """Renders template with given path and arguments.

    Parameters
    ----------
    path : str
        Path to template.
    kwargs : dict
        Keyword arguments to pass to template.

    Returns
    -------
    str
        rendered template
    """
    templates = current_app.config.get('TEMPLATES', None)
    if (templates is not None) and (path in templates):
        data_lst = templates[path]
        if not isinstance(data_lst, collections.Sequence):
            data_lst = [data_lst, ]
        for data in data_lst:
            dtype, value, filters = data['type'], data['value'], None
            if dtype == 'redirect.url_for':
                return redirect(url_for(value))
            elif dtype == 'redirect':
                return redirect(value)
            if 'filter' in data:
                filters = data['filter']
            if (filters is None) or eval(filters.format(**kwargs)):
                if dtype == 'string':
                    return render_template_string(value, **kwargs)
                else:
                    return flask_render_template(value, **kwargs)
    return flask_render_template(path, **kwargs)


class Pagination(object):
    def __init__(self, request=None):
        """Returns pagination parameters from request.

        Parameters
        ----------
        request : flask.Request
            Request object.

        Returns
        -------
        dict
            Pagination parameters.
        """
        if request is None:
            request = flask_request
        try:
            page = int(request.args['page'])
        except (KeyError, ValueError):
            page = 1
        if page < 1:
            page = 1
        self.page = page
        try:
            per_page = int(request.args['per_page'])
        except (KeyError, ValueError):
            per_page = 10
        if per_page < 1:
            per_page = 1
        self.per_page = per_page
        self.error_out = False

    def to_dict(self):
        """Returns pagination parameters as dictionary.

        Returns
        -------
        dict
            Pagination parameters.
        """
        return {
            'page': self.page,
            'per_page': self.per_page,
            'error_out': self.error_out,
        }
