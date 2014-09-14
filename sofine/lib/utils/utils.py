"""Provides utility functions used by sofine.
"""


import sys
import os
import imp
import sofine.lib.utils.conf as conf


def _load_plugin_module(module_name):
    module = None
    module_file = None
    try:
        module_file, module_path, desc = imp.find_module(module_name)
        module = imp.load_source(module_name, module_path, module_file)
    finally:
        if module_file:
            module_file.close()

    return module


# Create and return a proxy wrapper around a call to the URL provided
#  by the user in sofine.config
# TODO Document how to configure and use
# TODO Document this
# The API to clients writing HTTP plugins is as follows
#   1) Put base URL to plugins in sofine.conf FUTURE TODO - support multiple base endpoints
#   2) Plugin must expose two HTTP endpoints:
#      - parse_args - takes args=arg1,arg2 
#                     returns is_valid, parsed_args JSON object
#   3) - get_data - takes query string keys=key1,key2, ...
#                     returns sofine data structure: { key: [{attr_key: attr_val}, ...], ...}
class HttpPluginProxy(object):

    def __init__(self, plugin_name, plugin_group):
        from urllib import urlopen, urlencode 
        import json
        self._plugin_url = (conf.CUSTOM_HTTP_PLUGIN_URL + '/{0}' + '/{1}').format(plugin_name, plugin_group)
    
    
    def parse_args(self, args):
        ret = urllib.urlopen(self._plugin_url + 
                             '/parse_args?args=' + 
                             ','.join([urllib.urlencode(arg) for arg in args]))
        ret = json.loads(ret)
        is_valid = ret["is_valid"]
        parsed_args = ret["parsed_args"]
        return is_valid, parsed_args

    
    def get_data(self, keys, parsed_args):
        ret = urllib.urlopen(self._plugin_url + 
                             '/get_data?keys=' + 
                             ','.join([urllib.urlencode(key) for key in keys]) +
                             '&args=' + 
                             ','.join([urllib.urlencode(arg) for arg in args])) 
        ret = json.loads(ret)
        return ret 


def _load_plugin_http(plugin_name, plugin_group):
    return HttpPluginProxy(plugin_name, plugin_group)


def load_plugin_module(plugin_name, plugin_group=None):
    """
* `module_name` - `string`. The name of the plugin to load
* `plugin_group` - `string`. The name of the plugin directory of the plugin to load 
   
Loads a plugin from either the sofine default plugin directory or the plugin directory 
configured by the user in the `plugin_path` key of the `sofine.conf` file in the 
sofine project root. Loading first looks in the `plugin_path` and then in the sofine 
default plugin directory.

A plugin named `plugin_name` found in the plugin directory `plugin_group` is loaded. 

Returns an instance of the plugin module, not the plugin itself. This allows clients 
to declare module scope variables in plugins and use this method (wrapped in 
`runner`) to get an instance of the module to access the variables.
"""
    # conf only loads the base path, without plugin_group subdirectory
    # So always dynamically load the full plugin plath into sys.path
    #  if the call included a plugin_group, otherwise the call to load
    #  the plugin will fail
    base_plugin_path = conf.PLUGIN_BASE_PATH
    if plugin_group:
        base_plugin_path += ('/' + plugin_group)
    sys.path.insert(0, base_plugin_path)
    if conf.CUSTOM_PLUGIN_BASE_PATH:
        custom_plugin_base_path = conf.CUSTOM_PLUGIN_BASE_PATH
        if plugin_group:
            custom_plugin_base_path += ('/' + plugin_group)
        sys.path.insert(0, custom_plugin_base_path)

    ret = _load_plugin_module(plugin_name)
    
    # Didn't find plugin as a Python module so try to find HTTP plugin
    if not ret:
        ret = _load_plugin_http(plugin_name, plugin_group)

    return ret


def load_plugin(plugin_name, plugin_group):
    """
* `plugin_name` - `string`. The name of the plugin to load
* `plugin_group` - `string`. The name of the plugin directory of the plugin to load 

Loads a plugin from either the sofine default plugin directory or the plugin directory 
configured by the user in the `plugin_path` key of the `sofine.conf` file in the 
sofine project root. Loading first looks in the `plugin_path` and then in the sofine 
default plugin directory.

A plugin named `plugin_name` found in the plugin directory `plugin_group` is loaded. 
Note that here "loaded" means a reference to a new instance of an object of the plugin 
class type is returned.
"""
    # Each module is responsible for setting a variable named 'plugin' at
    #  module scope, set to the name of the module's plugin class.
    #  Also, plugins must only have a no-arg constructor.  Thus
    #  this call constructs and returns an instance of the plugin at this
    #  module_name and plugin_group.
    return load_plugin_module(plugin_name, plugin_group).plugin()


def has_stdin():
    return not sys.stdin.isatty()


def namespacer(plugin_group, plugin, name):
    """
* `plugin_group` - `string`. The name of the plugin directory
* `plugin` - `string`. The name of the plugin
* `name` - `string`. An attribute key name

A helper to enforce DRY. Used in the two places that namespace attribute keys which are 
appended to the attributes associated with the keys in the data set built by a sofine call. 
"""
    return plugin_group + '::' + plugin + '::' + name


def get_attr_keys(data):
    """Slice all the attribute lists, which are lists of single key/value dicts mapped to the keys 
in a sofine data set, to return the key from each dict in each list.
* `data` - `dict of string -> list of dict`. The data type of the attributes associated with a key in a 
returned data set."""
    out = []
    attrs_rows = data.values()
    for attrs_row in attrs_rows: 
        for attr in attrs_row:
            out.append(attr.keys()[0])
    return out


def get_attr_values(data):
    """Slice all the attribute lists, which are lists of single key/value dicts mapped to the keys 
in a sofine data set, to return the value from each dict in each list.
* `data` - `dict of string -> list of dict`. The data type of the attributes associated with a key in a 
returned data set."""
    out = []
    attrs_rows = data.values()
    for attrs_row in attrs_rows: 
        for attr in attrs_row:
            out.append(attr.values()[0])
    return out

