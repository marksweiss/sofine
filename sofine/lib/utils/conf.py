"""Loads global sofine configuration in from a configuration file. The file must be stored 
in the project root and must be called either `sofine.conf` or `example.sofine.conf`. If 
`sofine.conf` is found it will be used over `example.sofine.conf`.

Current supported configuration keys are:

* `plugin_path` - The path to the user's plugins directory. This can be any reachable path 
that sofine has permission to read.
* `rest_port` - The port for running the sofine REST server under the `localhost` domain. 
The default value is `10000` defined in `example.sofine.conf`.
"""

import inspect
import sys
import json
import os


CUSTOM_PLUGIN_BASE_PATH = None
"""The user-defined plugin directory. The idea is that users of sofine simply install the 
library, configure this value, and then can deploy, version control, write tests for and 
otherwise manage their plugins in a separate directory, which sofine CLI and REST calls 
transparently look in to load plugins. This value is defined in the JSON configuration file 
`sofine.conf` under the key `plugin_path`.
"""

REST_PORT = None
"""The port for running the sofine REST server under the `localhost` domain. This value 
is defined in the JSON configuration file `sofine.conf` under the key `rest_port`. The default 
value is defined in `example.sofine.conf` and will be used if the user doesn't override it in 
`sofine.conf`.
"""

def get_plugin_conf():
    plugin_conf_path = '/'.join(inspect.stack()[0][1].split('/')[:-4])

    plugin_conf = None
    try:
        plugin_conf = json.load(open(plugin_conf_path + '/sofine.conf'))
    except:
        pass

    print plugin_conf

    return plugin_conf


# Add the plugins direcgory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins'
sys.path.insert(0, PLUGIN_BASE_PATH) 

# Check environment variables for custom plugin path and REST port and prefer those if found
CUSTOM_PLUGIN_BASE_PATH = os.environ.get('SOFINE_PLUGIN_PATH')
if CUSTOM_PLUGIN_BASE_PATH:
    sys.path.insert(0, CUSTOM_PLUGIN_BASE_PATH) 
else:
    plugin_conf = get_plugin_conf()
    if plugin_conf:
        CUSTOM_PLUGIN_BASE_PATH = plugin_conf['plugin_path']
        sys.path.insert(0, CUSTOM_PLUGIN_BASE_PATH) 

if not CUSTOM_PLUGIN_BASE_PATH:
    print('Plugin Path not defined in SOFINE_PLUGIN_PATH environment variable or "plugin_path" key in "sofine.conf" in sofine root directory')

REST_PORT = os.environ.get('SOFINE_REST_PORT')
if REST_PORT:
    REST_PORT = int(REST_PORT)
else:
    plugin_conf = get_plugin_conf()
    REST_PORT = plugin_conf['rest_port']

if not REST_PORT:
    print('REST port not defined in SOFINE_REST_PORT environment variable or "rest_port" key in "sofine.conf" in sofine root directory')

