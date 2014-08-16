"""Plugin that wraps calling the Google search API.
"""


import urllib
import urllib2
import json
from sofine.plugins import plugin_base as plugin_base


def query_google_search(k):
    """
* `k` - `string`. The query term.

Helper that calls Google Search API with a query and returns JSON results set. 
Returns an array of JSON objects in the `['responseData']['results']` value  as 
described in the documentation for `get_child_schema`.
"""    
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}'.format(urllib.quote(k))
    ret = urllib2.urlopen(url)
    ret = ret.read()
    ret = json.loads(ret)
    
    if ret: 
        ret = {'results' : ret['responseData']['results']}
    else:
        ret = {'results' : []}
    
    return ret


def get_child_schema():
    """An optional function which returns the list of child keys that are associated
with the parent key `results` defined in `self.schema`.

This API returns an array of JSON objects, with the possible fields shown in the example.
Hence the return type is list of lists, because this plugin returns
a list of objects, each with this possible set of keys.

Returns:

    [['GsearchResultClass', 'unescapedUrl', 'url', 'visibleUrl', 'cacheUrl', 'title', 
    'titleNoFormatting', 'content']]

Example of one of the child objects in the array associated with `results`:

    {
        "GsearchResultClass": "GwebSearch",
        "cacheUrl": "http://www.google.com/search?q=cache:XhbIlCyrcXMJ:finance.yahoo.com",
        "content": "View the basic <b>AAPL</b> stock chart on Yahoo! Finance. Change the date range, chart type and compare Apple Inc. against other companies.",
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
        """
* `self.name = 'google_search_results'`
* `self.group = 'example'`
* `self.schema = ['results']`
* `self.adds_keys = False`
"""
        super(GoogleSearchResults, self).__init__()
        self.name = 'google_search_results'
        self.group = 'example'
        self.schema = ['results']
        self.adds_keys = False


    def get_data(self, keys, args):
        """
* `keys` - `list`. The list of keys to process.
* `args` - `'list`. Empty for this plugin.

Calls Google Search using their AJAX API to send a search query and return JSON.
"""
        return {k : query_google_search(k) for k in keys}

plugin = GoogleSearchResults 

