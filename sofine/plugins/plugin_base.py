"""Provides the default implementation of a plugin. All user plugins must derive from this
base class. For example implementations, see any of the plugins under `sofine/plugins/mock`, 
`sofine/plugins/example` or `sofine/plugins/default`.
"""


import sofine.lib.utils.utils as utils


class PluginBase(object):
    
    def __init__(self):
        """
* `self.name = None` 
* `self.group = None` 
* `self.schema = []`
* `self.adds_keys = False`

Creates the default attributes that all plugins must define. All plugins must derive from 
this base class.

They must set `self.name` and `self.group` and these must point to the name of the 
plugin module and the subdirectory in the plugin directory where the plugin can be found.

`self.schema` lists the attribute names that this plugin can associate with the keys it is passed 
in `get_data`. So the plugin can add namespaced versions of these attribute keys and values for 
each key to the attribute JSON object associated with each key in the data set built by the call 
sofine. This variable does not need to be set because it only exists to let clients of a plugin 
introspect the plugin by calling `get_schema` to see the attributes it can add. However, it is 
recommended that users creating plugins do define this.

`self.adds_keys` is also optional and also allows plugin clients to introspect the plugin, asking 
if it adds keys to data or just adds attributes to existing keys.
"""
        self.name = None
        self.group = None
        self.schema = []
        self.adds_keys = False


    def parse_args(self, argv):
        """Provides the default implementation for a simple plugin that takes no arguments.
"""
        is_valid = True
        return is_valid, argv


    def get_schema(self, args=None):
        """Provides the default implementation which calls the helper to namespace the 
list of attribute names in `self.schema.`

This should suffice for any plugin that knows its schema. Dynamic plugins, like `file_source` 
in the `standard` group, need to overload this method to set their schema property based 
on the data they retrieve.
"""
        return self.schema


    def get_namespaced_schema(self):
        """Returns the list of attribute keys in `self.schema` prepended with `self.group` 
and `self.name`, guaranteeing that each attribute key is uniquely namespaced.
"""
        return [utils.namespacer(self.group, self.name, attr) for attr in self.schema]

