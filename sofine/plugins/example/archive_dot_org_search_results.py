import urllib2
import json
import sofine.lib.utils.utils as utils


def _query_archive_dot_org(k):
    url = 'http://archive.org/advancedsearch.php?q={0}&output=json'.format(k)
    ret = urllib2.urlopen(url)
    ret = ret.read()
    ret = json.loads(ret)
    # Returns an array of JSON objects ("docs") in the ['response']['docs'] key
    # See get_schema() docstring below for more comlete documentation
    return {'docs' : ret['response']['docs']}


def get_data(keys, args):
    """Calls archive.org using their CGI query string API to send a search query and
return JSON."""
    data = {}
    for k in keys:
        data[k] = _query_archive_dot_org(k)
    return data


def parse_args(argv):
    """get_data() takes no arguments so this is a trivial pass-through."""
    is_valid = True
    return is_valid, argv


def adds_keys():
    """This data source cannot be the first in a chain of calls. It will add available 
attributes to those mapped to each key in the data arg passed to get_data()"""
    return False


def get_schema():
    return utils.schema_namespacer(
            utils.get_plugin_name(__file__), utils.get_plugin_group(__file__), 
            ['docs'])


def get_child_schema():
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

