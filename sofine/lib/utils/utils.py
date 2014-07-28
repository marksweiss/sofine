"""Provides utility functions used by sofine.
"""


import sys
import os
import imp
import sofine.lib.utils.conf as conf


def load_plugin(plugin_name, plugin_group):
    """
* `plugin_name` - `string`. The name of the plugin to load
* `plugin_group` - `string`. The name of the plugin directory of the plugin to load 

Loads a plugin from either the sofine default plugin directory or the plugin directory 
configured by the user in the `plugin_path` key of the `sofine.conf` file in the 
sofine project root. Loading first looks in the `plugin_path` and then in the sofine 
default plugin directory.

A plugin named `plugin_name` found in the plugin directory `plugin_group` is loaded. 
Note that here "loaded" means a reference to a new instance of an object of the plugin 
class type is returned.
"""
    # Each module is responsible for setting a variable named 'plugin' at
    #  module scope, set to the name of the module's plugin class.
    #  Also, plugins must only have a no-arg constructor.  Thus
    #  this call constructs and returns an instance of the plugin at this
    #  module_name and plugin_group.
    return load_plugin_module(plugin_name, plugin_group).plugin()


def load_plugin_module(module_name, plugin_group):
    """
* `module_name` - `string`. The name of the plugin to load
* `plugin_group` - `string`. The name of the plugin directory of the plugin to load 
   
Loads a plugin from either the sofine default plugin directory or the plugin directory 
configured by the user in the `plugin_path` key of the `sofine.conf` file in the 
sofine project root. Loading first looks in the `plugin_path` and then in the sofine 
default plugin directory.

A plugin named `plugin_name` found in the plugin directory `plugin_group` is loaded. 

Returns an instance of the plugin module, not the plugin itself. This allows clients 
to declare module scope variables in plugins and use this method (wrapped in 
`runner`) to get an instance of the module to access the variables.
"""
    sys.path.insert(0, conf.PLUGIN_BASE_PATH + '/' + plugin_group)
    if conf.CUSTOM_PLUGIN_BASE_PATH:
        sys.path.insert(0, conf.CUSTOM_PLUGIN_BASE_PATH + '/' + plugin_group)

    module = None
    module_file = None
    try:
        module_file, module_path, desc = imp.find_module(module_name)
        module = imp.load_source(module_name, module_path, module_file)
    finally:
        if module_file:
            module_file.close()

    return module


def has_stdin():
    return not sys.stdin.isatty()


def namespacer(plugin_group, plugin, name):
    """
* `plugin_group` - `string`. The name of the plugin directory
* `plugin` - `string`. The name of the plugin
* `name` - `string`. An attribute key name

A helper to enforce DRY. Used in the two places that namespace attribute keys which are 
appended to the attributes associated with the keys in the data set built by a sofine call. 
"""
    return plugin_group + '::' + plugin + '::' + name

