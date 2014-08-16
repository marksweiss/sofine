"""Plugin that wraps querying www.archive.org.
"""

import urllib
import urllib2
import json
from sofine.plugins import plugin_base as plugin_base


def get_child_schema(self):
    """An optional function which returns the list of child keys that are associated
with the parent key `docs` defined in `self.schema`.

This API returns an array of JSON objects, with the possible fields shown in the example.
Hence the return type is list of lists, because this plugin returns
a list of objects, each with this possible set of keys.

Returns:i

    [['year', 'title', 'description', 'mediatype', 'publicdate', 'downloads', 'week', 
    'month', 'identifier', 'format', 'collection', 'creator', 'score']]

Example of one of the child objects in the array associated with `docs`:

    {
        year: 1998,
        title: "AAPL CONTROL ROOM AERO ACOUSTIC PROPULSION LABORATORY AND CONTROL ROOM PERSONNEL",
        description: "AAPL CONTROL ROOM AERO ACOUSTIC PROPULSION LABORATORY AND CONTROL ROOM PERSONNEL",
        mediatype: "image",
        publicdate: "2009-09-17T17:14:53Z",
        downloads: 5,
        week: 0,
        month: 0,
        identifier: "GRC-C-1998-853",
        format: [
            "JPEG",
            "JPEG Thumb",
            "Metadata"
        ],
        collection: [
            "nasa",
            "glennresearchcentercollection"
        ],
        creator: [
            "NASA/Glenn Research Center"
        ],
        score: 2.617863
    }
"""
    return [['year', 'title', 'description', 'mediatype', 'publicdate', 'downloads', 'week',
             'month', 'identifier', 'format', 'collection', 'creator', 'score']]


def query_archive_dot_org(k):
    """
* `k` - `string`. The query term.

Helper that calls archive.org API with a query and returns JSON results set. 
Returns an array of JSON objects in the `['response']['docs']` value. 
"""    
    url = 'http://archive.org/advancedsearch.php?q={0}&output=json'.format(urllib.quote(k))
    ret = urllib2.urlopen(url)
    ret = ret.read()
    ret = json.loads(ret)
    if ret:
        ret = {'docs' : ret['response']['docs']}
    else:
        ret = {'docs' : []}

    return ret


class ArchiveDotOrgSearchResults(plugin_base.PluginBase):

    def __init__(self):
        """
* `self.name = 'archive_dot_org_search_results'`
* `self.group = 'example'`
* `self.schema = ['docs']`
* `self.adds_keys = False`
"""
        super(ArchiveDotOrgSearchResults, self).__init__()
        self.name = 'archive_dot_org_search_results'
        self.group = 'example'
        self.schema = ['docs']
        self.adds_keys = False
   

    def get_data(self, keys, args):
        """
* `keys` - `list`. The list of keys to process.
* `args` - `'list`. Empty for this plugin.

Calls archive.org using their CGI query string API to send a search query and
return JSON.
"""
        return {k : query_archive_dot_org(k) for k in keys}


plugin = ArchiveDotOrgSearchResults

