import sys
import os
import imp
import conf


def load_module(module_name, plugin_group):
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


def get_plugin_name(plugin_file):
    name = plugin_file.split('/')[-1:][0]
    name = name.split('.')[0]
    return name


def get_plugin_group(plugin_file):
    return os.path.dirname(plugin_file).split('/')[-1:][0]


def namespacer(plugin_group, plugin, name):
    return plugin_group + '::' + plugin + '::' + name


def schema_namespacer(plugin, plugin_group, attr_names):
    """Assumes that it is receiving the output of __file__ from a plugin as the value 
for the 'plugin' arg, and thus strips the file extension from that to prefix each schema 
value with it's plugin. This namespaces the attribute names returned by each plugin's 
get_schema() call to match the actual key names for attributes in the data returned. 
This is a bit cumbersome, but it makes the get_schema() output truly useful, to, for 
example, find all the attributes in a pipelined data set that came from a certain plugin."""
    return [namespacer(plugin_group, plugin, name) for name in attr_names]

