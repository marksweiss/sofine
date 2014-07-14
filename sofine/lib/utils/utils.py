import sys
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

