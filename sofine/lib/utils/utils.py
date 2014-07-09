import sys
import inspect
import imp


# Add the plugins direcgory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
sys.path.insert(0, '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins')


def load_module(module_name):
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
