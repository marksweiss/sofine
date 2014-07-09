import sys
import inspect
import imp


# Add the plugins direcgory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins'
sys.path.insert(0, PLUGIN_BASE_PATH) 


def load_module(module_name, plugin_group):
    plugin_path = PLUGIN_BASE_PATH + '/' + plugin_group  
    sys.path.insert(0, plugin_path)

    module = None
    module_file = None
    try:
        module_file, module_path, desc = imp.find_module(module_name)
        module = imp.load_source(module_name, module_path, module_file)
    except Exception as e:
        # TODO Real error logging
        print e.message   
    finally:
        if module_file:
            module_file.close()

    return module
