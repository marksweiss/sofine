from sofine.plugins import plugin_base as plugin_base
from optparse import OptionParser
import json



def get_keys(path):
    """Retrieves a set of keys found in the file named in the 'path' arg.
Keys must be written in a valid JSON object, which has a single key 
'keys' and a JSON array of valid JSON values for keys.  

Example: {"keys" : ["AAPL", "MSFT"]}

Provided as a helper to the plugin class and also as a convenience for clients 
to retrieve the keys found in a given file at 'path.' So, exposed here as a free
function. Clients may access it through the runner interface like so:
    mod = runner.get_plugin_module('file_source', 'standard')
    keys = mod.get_keys(path)
"""
    file_source_json = None
    with open(path) as f:
        file_source_json = json.load(f)
    return file_source_json['keys']


class FileSource(plugin_base.PluginBase):

    def __init__(self):
        self.name = 'file_source'
        self.group = 'standard'
        # This is a dynamic plugin for which adds_keys() is True but it only 
        #  provides keys to the data set, not attributes for those keys. So
        #  it's schema property is [] 
        self.schema = []
        # This plugin adds keys from it's file
        self.adds_keys = True


    def get_data(self, keys, args):
        """Loads a set of keys found in the file named in the 'path' arg. Ignores any keys 
passed in -- this is a pure data source. Keys must be written in a valid JSON object, 
which has a single key 'keys' and a JSON array of valid JSON values for keys.  

Example: {"keys" : ["AAPL", "MSFT"]}
"""
        path = args[0]
        new_keys = get_keys(path)
        data = dict.fromkeys(new_keys, {})
        return data


    def parse_args(self, argv):
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


plugin = FileSource

