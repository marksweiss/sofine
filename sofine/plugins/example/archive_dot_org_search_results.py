import urllib2
import json
from sofine.plugins import plugin_base as plugin_base


def get_child_schema(self):
    """An optional function to let users query this property of this plugin, which 
returns a nested value which is itself a JSON object with these keys.

This API returns an array of JSON objects, with the possible fields shown in the example.
Hence the return time for this get_schema is a list of lists, because this plugin returns
a list of objects, each with this possible set of keys.

Example:
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
    url = 'http://archive.org/advancedsearch.php?q={0}&output=json'.format(k)
    ret = urllib2.urlopen(url)
    ret = ret.read()
    ret = json.loads(ret)
    # Returns an array of JSON objects ("docs") in the ['response']['docs'] key
    # See get_schema() docstring below for more comlete documentation
    if ret:
        ret = {'docs' : ret['response']['docs']}
    else:
        ret = {'docs' : []}

    return ret


class ArchiveDotOrgSearchResults(plugin_base.PluginBase):

    def __init__(self):
        self.name = 'archive_dot_org_search_results'
        self.group = 'example'
        self.schema = ['docs']
        self.adds_keys = False
   

    def get_data(self, keys, args):
        """Calls archive.org using their CGI query string API to send a search query and
return JSON."""
        data = {}
        for k in keys:
            data[k] = query_archive_dot_org(k)
        return data


plugin = ArchiveDotOrgSearchResults

