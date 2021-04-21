from flask import current_app, render_template_string, render_template as flask_render_template, redirect, url_for


def render_template(path, **kwargs):
    templates = current_app.config.get('templates', None)
    if (templates is not None) and (path in templates):
        data = templates[path]
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
