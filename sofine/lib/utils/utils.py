import sys
import os
import imp
import sofine.lib.utils.conf as conf


def load_plugin(module_name, plugin_group):
    return load_plugin_module(module_name, plugin_group).plugin()


def load_plugin_module(module_name, plugin_group):
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

    # Each module is responsible for setting a variable named 'plugin' at
    #  module scope, set to the name of the module's plugin class.
    #  Also, plugins must only have a no-arg constructor.  Thus
    #  this call constructs and returns an instance of the plugin at this
    #  module_name and plugin_group.
    return module


def has_stdin():
    return not sys.stdin.isatty()


def namespacer(plugin_group, plugin, name):
    return plugin_group + '::' + plugin + '::' + name


