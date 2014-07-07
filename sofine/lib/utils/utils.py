import sys
import inspect
# I know. Ouch. This is apparently what it takes to dynamically load
#  modules in Python. At least it's wrapped up in a library, where it belongs
sys.path.insert(0, '/'.join(inspect.stack()[0][1].split('/')[:-2]))
import imp


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
