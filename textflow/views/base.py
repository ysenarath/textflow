"""Base view for textflow."""
import collections

from flask import (
    current_app,
    render_template_string,
    render_template as flask_render_template,
    redirect, url_for
)

__all__ = [
    'render_template',
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
