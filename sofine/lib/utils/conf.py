import inspect
import sys
import json


# Add the plugins direcgory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins'
sys.path.insert(0, PLUGIN_BASE_PATH) 

CUSTOM_PLUGIN_BASE_PATH = None
try:
    plugin_conf = json.load(open('/'.join(inspect.stack()[0][1].split('/')[:-4]) + '/plugin.conf'))
    CUSTOM_PLUGIN_BASE_PATH = plugin_conf['plugin_path']
    sys.path.insert(0, CUSTOM_PLUGIN_BASE_PATH) 
except:
    pass

if not CUSTOM_PLUGIN_BASE_PATH:
    try:
        plugin_conf = json.load(open('/'.join(inspect.stack()[0][1].split('/')[:-4]) + '/example.plugin.conf'))
        CUSTOM_PLUGIN_BASE_PATH = plugin_conf['plugin_path']
        sys.path.insert(0, CUSTOM_PLUGIN_BASE_PATH) 
    except:
        pass
