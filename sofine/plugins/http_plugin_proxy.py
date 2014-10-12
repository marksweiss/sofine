"""
This class is used by `sofine` to generate a proxy object around any HTTP plugin. `sofine`
dynamically creates the object based on the value in the environment variable 
SOFINE_HTTP_PLUGIN_URL and the plugin name and plugin group in the call. This wrapper
simply lets the existing mechanism to run plugins call a Python object with the same
API as Python plugins.

The second important function of this class is that it depends on and expects that 
all HTTP plugins will conform to the API for their return data types as defined in the
documentation for `sofine`. In particular, all of the public methods expect that the return
values from calling an HTTP plugin will have keys with designated names.
"""


import sofine.lib.utils.conf as conf
from urllib import urlopen, urlencode 
import json


class HttpPluginProxy(object):

    def __init__(self):
        self._plugin_url = ''

   
    # Clunky but we have to have a no-arg constructor to conform to the
    #  way utils loads modules. It needs a reference to a class with a no-arg ctor.
    # The only place this plugin proxy is instantiated is internally in utils.load_module()
    #  anyway, so this slight wart is encapsulated from users
    def set_plugin_url(self, plugin_name, plugin_group):
        self._plugin_url = (conf.CUSTOM_HTTP_PLUGIN_URL + '/{0}' + '/{1}').format(plugin_name, plugin_group)
    
    
    def _urlopen(self, url):
        ret = urlopen(url)
        ret = ret.read()
        ret = json.loads(ret)
        return ret


    def parse_args(self, args):
        qs_args = ','.join([urlencode({'x' : arg}).split('=')[1] for arg in args])
        ret = self._urlopen(self._plugin_url + '/parse_args?args=' + qs_args)
        is_valid = ret["is_valid"]
        parsed_args = ret["parsed_args"]
        return is_valid, parsed_args

    
    def get_data(self, keys, parsed_args):
        """
* `keys`. An array of keys for a `sofine` data retrieval
* `parsed_args` - an array of args to use in a data retrieval call

Proxy wrapper for retrieving data from an HTTP plugin. Calls a pliugin's _required_ `get_data` method. Transforms `keys` and `parsed_args` values into the required query string format that HTTP plugins must expect and support.

This is a very thin proxy with no business logic of its own other than constructing plugin calls to spec.
"""
        qs_keys = ','.join([urlencode({'x' : key}).split('=')[1] for key in keys])
        qs_args = ','.join([urlencode({'x' : arg}).split('=')[1] for arg in parsed_args])
        ret = self._urlopen(self._plugin_url + 
                '/get_data?keys=' + qs_keys + 
                '&args=' + qs_args)
        return ret 

    def get_schema(self):
        """
Proxy wrapper for retrieving the schema of data returned by an HTTP plugin.

This is a very thin proxy with no business logic of its own other than constructing plugin calls to spec.
"""
        ret = self._urlopen(self._plugin_url + '/get_schema')
        ret = ret["schema"]
        return ret


    def adds_keys(self):
        """
Proxy wrapper for discovering whether an HTTP plugin an add keys when the plugin is called
as part of a chain of `sofine` plugins in one `get_data` call.

This is a very thin proxy with no business logic of its own other than constructing plugin calls to spec.
"""
        ret = self._urlopen(self._plugin_url + '/adds_keys')
        ret = ret["adds_keys"]
        return ret


    # utils.load_module() calls a function plugin(). For Py plugins this is reference
    #  to the class placed in the module as an attribute plugin = class_name. So
    #  it amounts to constructing an instance of the plugin. Here we need to pass
    #  back an already constructed proxy object, bound to plugin_name and group
    #  because of the order of which things happen in utils. So we just provide
    #  a different implementation of plugin() which will resolve against the object
    #  already returned and just passes back a pointer to itself
    def plugin(self):
        return self

