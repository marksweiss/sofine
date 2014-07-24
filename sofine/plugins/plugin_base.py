import sofine.lib.utils.utils as utils


class PluginBase(object):
    
    def __init__(self):
        """The default implementation just returns the default value for the attribute. 
This is the correct behavior for a simple plugin that doesn't add keys but simply adds 
name/value attribute data to the keys it receives. A plugin that does add keys should simply 
override the default value for 'self.adds_keys' in '__init__()'."""
        self.name = None
        self.group = None
        self.schema = []
        self.adds_keys = False


    def get_schema(self, args=None):
        """The default implementation is to just call the helper to namespace the 
list of attribute names in self.schema. Dynamic plugins, like 'file_source' in the 
'standard' group, need to overload get_schema() to set their schema property as 
needed and then themselves call get_namespaced_schema()."""
        return self.get_namespaced_schema()


    def get_namespaced_schema(self):
        """Assumes that it is receiving the output of __file__ from a plugin as the value 
for the 'plugin' arg, and thus strips the file extension from that to prefix each schema 
value with it's plugin. This namespaces the attribute names returned by each plugin's 
get_schema() call to match the actual key names for attributes in the data returned. 
This is a bit cumbersome, but it makes the get_schema() output truly useful, to, for 
example, find all the attributes in a pipelined data set that came from a certain plugin."""
        return [utils.namespacer(self.group, self.name, attr) for attr in self.schema]

