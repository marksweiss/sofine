import inspect
import sys
import json


# Add the plugins direcgory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins'
sys.path.insert(0, PLUGIN_BASE_PATH) 


plugin_conf_path = '/'.join(inspect.stack()[0][1].split('/')[:-4])

plugin_conf = None
CUSTOM_PLUGIN_BASE_PATH = None
REST_PORT = None
try:
    plugin_conf = json.load(open(plugin_conf_path + '/sofine.conf'))
except:
    pass

if not plugin_conf:
    try:
        plugin_conf = json.load(open(plugin_conf_path + '/example.sofine.conf'))
    except:
        pass

if plugin_conf:
    CUSTOM_PLUGIN_BASE_PATH = plugin_conf['plugin_path']
    sys.path.insert(0, CUSTOM_PLUGIN_BASE_PATH) 
    REST_PORT = plugin_conf['rest_port']
