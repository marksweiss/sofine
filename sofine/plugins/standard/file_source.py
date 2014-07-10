from collections import defaultdict as defaultdict
from optparse import OptionParser
import json


def get_data(data, args):
    """Loads a set of keys found in the file named in the 'path' arg. Keys 
must be written in a valid JSON object, which has a single key "keys" and a JSON array of
valid JSON values for keys. Note that JSON strings are only valid if double-quoted.

Example: {"keys" : ["AAPL", "MSFT"]}
"""
    path = args[0]
    keys = _get_keys(path)
    
    data = defaultdict(dict)
    for k in keys:
        data[k]
    
    return data


def parse_args(argv):
    usage = """
[-p|--path] - Path to the file listing the keys to load into this data source.
"""
    parser = OptionParser(usage=usage)

    parser.add_option("-p", "--path", 
                      action="store", dest="path",
                      help="Path to the file listing the keys to load into this data source. Required.") 

    (opts, args) = parser.parse_args(argv)
    
    is_valid = True
    if not opts.path:
        print "Invalid argument error."
        print """
Your args:  
  path {0}""".format(opts.path)
        print usage
        is_valid = False

    return is_valid, [opts.path]


def is_source():
    """This data source must be the first call in a chain of calls. It will ignore 
any data passed to it, and it will return data with a set of keys and attributes 
matching those found in the file it reads from."""
    return True


def get_schema(args):
    """The set of all possible attribute keys returned for each key from this data
source. This data source always returns the attribute keys listed in a file source. 
However, that file source can be any argument passed to get_data(), so there is 
no set schema that can be returned. So, this method takes an optional argument 
with a pat. If path is provided, the method returns the list of attributes in 
that file source. If path is not provided, it returns an empty list."""
    path = args[0]
    return _get_keys(path)


def _get_keys(path):
    file_source_json = None
    with open(path) as f:
        file_source_json = json.load(f)
    return file_source_json['keys']
