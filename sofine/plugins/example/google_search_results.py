import urllib2
import json
from sofine.plugins import plugin_base as plugin_base


def query_google_search(k):
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}'.format(k)
    ret = urllib2.urlopen(url)
    ret = ret.read()
    ret = json.loads(ret)
    # Returns an array of JSON objects ("docs") in the ['responseData']['results'] key
    # See get_schema() docstring below for more comlete documentation
    
    if ret: 
        ret = {'results' : ret['responseData']['results']}
    else:
        ret = {'results' : []}
    
    return ret


def get_child_schema():
    """An optional function to let users query this property of this plugin, which 
returns a nested value which is itself a JSON object with these keys.

This API returns an array of JSON objects, with the possible fields shown in the example.
Hence the return time for this get_schema is a list of lists, because this plugin returns
a list of objects, each with this possible set of keys.

Example:
{
    "GsearchResultClass": "GwebSearch",
    "cacheUrl": "http://www.google.com/search?q=cache:XhbIlCyrcXMJ:finance.yahoo.com",
    "content": "View the basic <b>AAPL</b> stock chart on Yahoo! Finance. Change the date range, \nchart type and compare Apple Inc. against other companies.",
    "title": "<b>AAPL</b>: Summary for Apple Inc.- Yahoo! Finance",
    "titleNoFormatting": "AAPL: Summary for Apple Inc.- Yahoo! Finance",
    "unescapedUrl": "http://finance.yahoo.com/q?s=AAPL",
    "url": "http://finance.yahoo.com/q%3Fs%3DAAPL",
    "visibleUrl": "finance.yahoo.com"
}
"""
    return [['GsearchResultClass', 'unescapedUrl', 'url', 'visibleUrl', 'cacheUrl', 'title', 
             'titleNoFormatting', 'content']]


class GoogleSearchResults(plugin_base.PluginBase):

    def __init__(self):
        self.name = 'google_search_results'
        self.group = 'example'
        self.schema = ['results']
        self.adds_keys = False


    def get_data(self, keys, args):
        """Calls Google Search using their AJAX API to send a search query and return JSON."""
        data = {}
        for k in keys:
            data[k] = query_google_search(k)
        return data


    def parse_args(self, argv):
        """get_data() takes no arguments so this is a trivial pass-through."""
        is_valid = True
        return is_valid, argv


plugin = GoogleSearchResults 

