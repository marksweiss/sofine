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

    def __init__(self, plugin_name, plugin_group):
        self._plugin_url = (conf.CUSTOM_HTTP_PLUGIN_URL + '/{0}' + '/{1}').format(plugin_name, plugin_group)
    

    def _urlopen(self, url):
        ret = urllib.urlopen(url)
        ret = ret.read()
        ret = json.loads(ret)
        return ret


    def parse_args(self, args):
        ret = self._urlopen(self._plugin_url + 
                            '/parse_args?args=' + 
                            ','.join([urllib.urlencode(arg) for arg in args]))
        is_valid = ret["is_valid"]
        parsed_args = ret["parsed_args"]
        return is_valid, parsed_args

    
    def get_data(self, keys, parsed_args):
        return self._urlopen(self._plugin_url + 
                             '/get_data?keys=' + 
                             ','.join([urllib.urlencode(key) for key in keys]) +
                             '&args=' + 
                             ','.join([urllib.urlencode(arg) for arg in args])) 


    def get_schema(self):
        ret = self._urlopen(self._plugin_url + 
                            '/get_schema')
        schema = ret["schema"]
        return schema


    def adds_keys(self):
        ret = self._urlopen(self._plugin_url + 
                            '/adds_keys')
        adds_keys = ret["adds_keys"]
        return adds_keys

