""" Plugin manager enables any class to be registered to be used in an application. """

__all__ = [
    'PluginManager'
]


class PluginManager:
    def __init__(self):
        self._plugins = dict()

    def list_names(self, category=None):
        """List names of plugins for the provided `category`.

        :param category: ident of project or type of project
        :return: list of names of data-sets for project
        """
        if category is not None and category in self._plugins:
            return list(self._plugins[category].keys())
        return []

    def get_plugin(self, category, name=None):
        """Gets plugin by provided `category`.

        :param category: category of plugin
        :param name: name of project
        :return: plugin object
        """
        name = 'default' if name is None else name
        if category is not None and category in self._plugins:
            if name in self._plugins[category]:
                name = 'default'
            if name in self._plugins[category]:
                return self._plugins[category][name]
            else:
                return None
        return None

    def register(self, category, name=None):
        """Register plugin under provided category.

        :param category: category of plugin.
        :param name: name of plugin under category.
        :return: decorator
        """
        name = 'default' if name is None else name

        def decorator(cls):
            if category is not None:
                if category not in self._plugins:
                    self._plugins[category] = dict()
                self._plugins[category].update({name: cls})
            return cls

        return decorator
