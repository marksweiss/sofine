import sofine.lib.utils.conf as conf
from urllib import urlopen, urlencode 
import json


# Create and return a proxy wrapper around a call to the URL provided
#  by the user in sofine.config or environment var
# TODO Document how to configure and use
# TODO Document this
# The API to clients writing HTTP plugins is as follows
#   1) Put base URL to plugins in sofine.conf FUTURE TODO - support multiple base endpoints
#   2) Plugin must expose two HTTP endpoints:
#      - parse_args - takes args=arg1,arg2 
#                     returns is_valid, parsed_args JSON object
#   3) - get_data - takes query string keys=key1,key2, ...
#                     returns sofine data structure: { key: [{attr_key: attr_val}, ...], ...}

# BONUS TODO
# Write example plugins in ruby, C, C++, node js, node coffee, Java, Go, Perl
# Redo ystockquotelib and Google Search API in each language

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
        
        # TEMP DEBUG
        print "PLUGIN URL"
        print (self._plugin_url + '/parse_args?args=' + qs_args)
        
        
        ret = self._urlopen(self._plugin_url + '/parse_args?args=' + qs_args)
        
        # TEMP DEBUG
        print "RET"
        print ret
        
        is_valid = ret["is_valid"]
        parsed_args = ret["parsed_args"]


        # TEMP DEBUG
        print "RET SPLIT"
        print is_valid
        print parsed_args

        return is_valid, parsed_args

    
    def get_data(self, keys, parsed_args):
        qs_keys = ','.join([urlencode({'x' : key}).split('=')[1] for key in keys])
        qs_args = ','.join([urlencode({'x' : arg}).split('=')[1] for arg in parsed_args])
        
        
        # TEMP DEBUG
        print "GET DATA URL"
        print (self._plugin_url + 
                '/get_data?keys=' + qs_keys + 
                '&args=' + qs_args)
        
        ret = self._urlopen(self._plugin_url + 
                '/get_data?keys=' + qs_keys + 
                '&args=' + qs_args)
        
        # TEMP DEBUG
        print "GET DATA RET"
        print ret
        
        
        return ret 

    def get_schema(self):
        ret = self._urlopen(self._plugin_url + '/get_schema')
        ret = ret["schema"]
        return ret


    def adds_keys(self):
        ret = self._urlopen(self._plugin_url + '/adds_keys')
        ret = ret["adds_keys"]
        return ret


    # Oh man this is a hack
    # utils.load_module() calls a function plugin(). For Py plugins this is reference
    #  to the class placed in the module as an attribute plugin = class_name. So
    #  it amounts to constructing an instance of the plugin. Here we need to pass
    #  back an already constructed proxy object, bound to plugin_name and group
    #  because of the order of which things happen in utils. So we just provide
    #  a different implementation of plugin() which will resolve against the object
    #  already returned and just passes back a pointer to itself
    def plugin(self):
        return self

