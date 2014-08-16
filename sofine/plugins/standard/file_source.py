from sofine.plugins import plugin_base as plugin_base
from optparse import OptionParser
import json



def get_keys(path):
    """
* `path` - `string`. The path to the file_source configuration file

Retrieves a set of keys found in the file named in the `path` arg.
Keys must be written in a valid JSON object, which has a single key 
`keys` and a JSON array of valid JSON values for keys.  

    // Example 
    {"keys" : ["AAPL", "MSFT"]}

Provided as a helper to the plugin class and also as a convenience for clients 
to retrieve the keys found in a given file at `path.` A common use case might be to 
store a list of keys at `path` and start a chained sofine call with the call to 
`file_source` to retrieve a static set of keys to then pass to other plugins that 
don't add keys themselves but just retrieve attributes for the keys passed to them.
"""
    file_source_json = None
    with open(path) as f:
        file_source_json = json.load(f)
    return file_source_json['keys']


class FileSource(plugin_base.PluginBase):
    
    def __init__(self):
        """
* `self.name = 'file_source'`
* `self.group = 'standard'`
* `self.schema = []`

This is a dynamic plugin for which adds_keys() is True but it only 
provides keys to the data set, not attributes for those keys. So
it's schema property is [].

* `self.adds_keys = True`

This plugin adds keys from it's file.
"""     
        super(FileSource, self).__init__()
        self.name = 'file_source'
        self.group = 'standard'
        self.schema = []
        self.adds_keys = True


    def get_data(self, keys, args):
        """
* `keys` - `list`. The list of keys to process. Should be empty for this plugin which 
in any case will ignore the argument.
* `args` - `'list`. The args for calling this plugin. There is one, the path to the 
file with the keys to be retrieved.

Loads a set of keys found in the file named in the `path` arg, which
is the first and only element in `args`.

    // Example: 
    {"keys" : ["AAPL", "MSFT"]}
"""
        path = args[0]
        new_keys = get_keys(path)
        data = dict.fromkeys(new_keys, {})
        return data


    def parse_args(self, argv):
        """`[-p|--path]` - Path to the file listing the keys to load into this data source.
"""
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

