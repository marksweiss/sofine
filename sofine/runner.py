"""
This module is the main driver for calls to plugins from the CLI interface. 
It also has all of the scaffolding and wrapper functions required to generically invoke 
and run any of the supported plugin methods in the plugin interface for any plugin 
using just the plugin name, plugin group and call args.
"""

import sofine.lib.utils.utils as utils
import sofine.lib.utils.conf as conf
from optparse import OptionParser
import json
import sys


def get_data(data, data_source, data_source_group, data_source_args):
    """
* `data` - `dict`. A dict of keys and associated array of dicts of attribute keys and values. May be empty. 
Any data collected by this call with append new keys and values to `data`, and append new attribute keys 
and values for existing keys into the array of attribute key/attribute value (single-entry) dicts 
associated with that key. Also, if this call is invoked from a piped command line call piping to sofine, 
that will be detected and `data` will be read from `stdin`, overriding whatever value is passed in for this arg.
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.
* `data_source_args` - `list`. The args for the plugin call, in `argv` format with alternating elements 
referring to argument names and argument values.
* `use_namespaced_attrs` - Defaults to False. Prepend all attribute keys from all plugin calls with the plugin name and plugin
group to guarantee the key name is unique in the returned data set.

Main driver function for retrieving data from a plugin. Calls a plugin's _required_ `get_data` method. 
Takes a list of data_sources and a list of argument lists to call when calling each data_source. 
Can be called directly or from `main` if this module was instantiated from the command line.

This method operates based on the core data aggregation semantics of the library:

* If this is the first call in the chain, data is empty, so just fill it with the return of this call
* If there is already data, add any new keys retrieved and add attribute key/value pairs associated 
with any new or existing keys 
is True. 
* The set of keys on each call is the union of all previously collected keys
* The set of attributes associated with each key is the union of all previously collected attribute/value
 pairs collected for that key

Output looks like this:
    
    {"key_1" : [{"attr_name_1" : value}, {"attr_name_2" : value}, {"attr_name_1, value}],
    "key_2" : ...
    }

"""
    plugin = utils.load_plugin(data_source, data_source_group)
    is_valid, parsed_args = plugin.parse_args(data_source_args)
    if not is_valid:
        raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))
    
    new_data = plugin.get_data(data.keys(), parsed_args)

    if len(new_data.keys()) > 0:
        for k in new_data.keys():
            # Convert returned dict of attributes into a list of individual dicts. This allows all data
            #  from all plugins to be added to the output without needing namespacing to prevent attributed
            #  keys from overwriting each other. Namespacing can optionally be turned on by the caller.
            new_data_list = [{name : val} for name, val in new_data[k].iteritems()]
            if k in data:
                data[k] += new_data_list
            else:
                data[k] = new_data_list 
    
    return data


def get_namespaced_data(data, data_source, data_source_group, data_source_args):
    """As in `get_data`, but each attribute dict in each array of attribute dicts that is the value of each key 
in the data set is prepended with the plugin name and plugin group. 

Namespaced output looks like this:
    
    {"key_1" : [{"plugin_group_A::plugin_1::attr_name_1" : value}, 
                {"plugin_group_A::plugin_1::attr_name_2" : value},
                {"plugin_group_B::plugin_1::attr_name_1" : value}],
    "key_2" : ...
    }
"""
    data = get_data(data, data_source, data_source_group, data_source_args)
    # Take the data returned, get the list of dicts associated with each key, for each attribute key in each
    #  attribute dict in each list of dicts, creat the namespaced key. Insert a new attribute dict into the list
    #  over the old one with the namespaced key and the same value
    for attrs in data.values():
        for j in range(0, len(attrs)):
            attr = dict(attrs[j])
            attr_key = utils.namespacer(data_source_group, data_source, attr.keys()[0])
            attr_val = attr.values()[0]
            attrs[j] = {attr_key : attr_val}
    
    return data


def _validate_get_data_batch(data_sources, data_source_groups, data_source_args, fn_name):
    if len(data_sources) != len(data_source_args) or \
            len(data_sources) != len(data_source_groups) or \
            len(data_source_groups) != len(data_source_args):
        raise ValueError("""Call to runner.{0}() had different lengths for 
data_sources (len == {1}), 
data source_groups (len == {2}) and 
data_source_args (len == {3)}""".format(fn_name, len(data_sources), len(data_source_groups), len(data_source_args)))


def get_data_batch(data, data_sources, data_source_groups, data_source_args):
    """
* `data` - `dict`. A dict of keys and associated array of dicts of attribute keys and values. May be empty. 
Any data collected by this call with append new keys and values to `data`, and append new attribute keys 
and values for existing keys into the dict associated with that key. 
* `data_source` - `list`. A list of names of plugins being called.
* `data_source_group` - `list`.  A list of names of plugin groups for the plugins being called.
* `data_source_args` - `list of list`. A list of lists of args for the plugin calls, in argv format with alternating elements 
referring to argument names and argument values.

Convenience wrapper for users of sofine as a Python library. This function lets a user pass in 
a list of data sources, a list of plugin groups and a list of lists of arguments for each plugin call. 
Note that the elements must be in order in each argument: data source name in position 0 must match 
data source group in position 0 and the list of args for that call in `data_source_args[0]`.
"""
    _validate_get_data_batch(data_sources, data_source_groups, data_source_args, 'get_data_batch')

    for j in range(0, len(data_sources)):
        data = get_data(data, data_sources[j], data_source_groups[j], data_source_args[j])
    
    return data


def get_namespaced_data_batch(data, data_sources, data_source_groups, data_source_args):
    """As in `get_data_batch`, but each attribute dict in each array of attribute dicts that is the value of each key 
in the data set is prepended with the plugin name and plugin group. All plugins called in the batch call will 
namespace the attributes they contribute to the final data set returned.

Namespaced output looks like this:
    
    {"key_1" : [{"plugin_group_A::plugin_1::attr_name_1" : value}, 
                {"plugin_group_A::plugin_1::attr_name_2" : value},
                {"plugin_group_B::plugin_1::attr_name_1" : value}],
    "key_2" : ...
    }
"""
    _validate_get_data_batch(data_sources, data_source_groups, data_source_args, 'get_namespaced_data_batch')

    for j in range(0, len(data_sources)):
        data = get_namespaced_data(data, data_sources[j], data_source_groups[j], data_source_args[j])
    
    return data


def _get_schema(get_schema_call, parse_args_call, data_source, data_source_group, args):
    plugin = utils.load_plugin(data_source, data_source_group)
    
    schema = None
    if not args:
        schema = get_schema_call() 
    else:
        is_valid, parsed_args = parse_args_call(args)
        if not is_valid:
            raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))
        schema = get_schema_call(parsed_args)
   
    return {"schema" : schema} 


def get_schema(data_source, data_source_group, args=None):
    """
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.
* `args` - `any`. This is a bit of a hack, but basically there are use cases that could require args in 
order to figure out the schema of available fields. Maybe a plugin wraps access to a data store that allows 
arbitary or varying schemas per document retrieved. Or maybe, like the included `standard.file_source` 
plugin, it wraps access to a config that can provide an arbitrary list of fields.

This returns the value for a plugin's _optional_ (but highly recommended) `self.schema` attribute. 
This method lets plugin users introspect the plugin to ask what schema fields it provides, that is, what 
set of attribute keys can it to the attributes dict for each key in data.

Note that the default implementation is provided by `PluginBase` and it returns a properly namespaced list 
of attribute keys. All the plugin creator has to do is set the `self.schema` attribute of their plugin to a 
list of strings of the attribute keys it can return.

Not all data sources gurarantee they will return all attribute keys for each key in data, and not 
all data sources guarantee they will return the same set of attribute keys for each key in data in 
one returned data set.
"""
    plugin = utils.load_plugin(data_source, data_source_group)
    return _get_schema(plugin.get_schema, plugin.parse_args, data_source, data_source_group, args)


def get_namespaced_schema(data_source, data_source_group, args=None):
    """As in `get_schema` except that the schema attribute keys returned are prepended with the `data_source` and 
`data_source_group`.
"""
    plugin = utils.load_plugin(data_source, data_source_group)
    return _get_schema(plugin.get_namespaced_schema, plugin.parse_args, data_source, data_source_group, args)


def parse_args(data_source, data_source_group, data_source_args):
    """
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.
* `data_source_args` - `list`. The args for the plugin call, in `argv` format with alternating elements 
referring to argument names and argument values.

A wrapper which calls a plugin's _required_ `parse_args` method. This method must parse arguments the plugin's `get_data` 
call requires, with the arguments in argv format with alternating elements referring to argument 
names and argument values.

The method is also responsible for validating arguments and returning a boolean `is_valid` as well as the 
parsed (and possibly modified) args.
"""
    plugin = utils.load_plugin(data_source, data_source_group)
    is_valid, parsed_args = plugin.parse_args(data_source_args)
    return {"is_valid" : is_valid, "parsed_args" : parsed_args}


def adds_keys(data_source, data_source_group):
    """
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.

A wrapper which calls a plugin's _optional_ (but recommended) `adds_keys` method. This introspection method 
lets plugin users ask whether a plugin adds its own keys to the `data` output or simply adds key/value 
attributes to the dicts being built by sofine for each key in `data`.
"""
    plugin = utils.load_plugin(data_source, data_source_group)
    adds_keys = plugin.adds_keys
    return {"adds_keys" : adds_keys}


def get_plugin_module(data_source, data_source_group):
    """
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.
    
Convenience function for clients to get an instance of a plugin module. 
This lets plugin implementers expose free functions in the module and have client 
code be able to access them.
"""
    return utils.load_plugin_module(data_source, data_source_group)


def get_plugin(data_source, data_source_group):
    """
* `data_source` - `string`. The name of the plugin being called.
* `data_source_group` - `string`.  The name of the plugin group for the plugin being called.

Convenience function for clients to get an instance of a plugin. 
This lets plugin implementers expose free functions in the module and have client 
code be able to access them.
"""
    return utils.load_plugin(data_source, data_source_group)


def _parse_runner_args(args):
    data_source = None
    data_source_group = None
    action = None

    def parse_runner_arg(args, arg_flags):
        ret = None
            
        def try_arg_flag(arg_flag):
            e = ''
            i = -1
            try:
                i = args.index(arg_flag)
            except ValueError:
                e = 'Required argument {0} not found in command line argument list passed to runner.main()'.format(arg_flag)
            if i == len(args) - 1:
                e = 'Value for required argument {0} not found in command line argument list passed to runner.main()'.format(arg_flag)

            return e, i

        # Try twice if necessary, for each of the two forms of the arg flag
        err, idx = try_arg_flag(arg_flags[0])
        if err:
            err, idx = try_arg_flag(arg_flags[1])
        # Flag was found, value for it parsed, and flag and value removed from args
        if not err:
            ret = args[idx + 1]
            del args[idx + 1]
            del args[idx]

        return err, ret
      
    # Parse for both versions of required flags and raise error if not found
    err, data_source = parse_runner_arg(args, ['--SF-s', '--SF-data-source'])
    if err: raise ValueError(err)
    err, data_source_group = parse_runner_arg(args, ['--SF-g','--SF-data-source-group'])
    if err: raise ValueError(err)
    # For optional argument, don't throw if not found, just set default value
    err, action = parse_runner_arg(args, ['--SF-a', '--SF-action'])
    if err:
        action = 'get_data'

    return data_source, data_source_group, action, args


def _run_action(action, ret, data_source, data_source_group, data_source_args):
    if action == 'get_data':
        ret = get_data(ret, data_source, data_source_group, data_source_args)
    if action == 'get_namespaced_data':
        ret = get_namespaced_data(ret, data_source, data_source_group, data_source_args)
    elif action == 'get_schema':
        ret = get_schema(data_source, data_source_group, data_source_args)
    elif action == 'get_namespaced_schema':
        ret = get_namespaced_schema(data_source, data_source_group, data_source_args)
    elif action == 'adds_keys':
        ret = adds_keys(data_source, data_source_group)
    elif action == 'parse_args':
        ret = parse_args(data_source, data_source_group, data_source_args)

    return ret


def main(argv):
    """Entry point if called from the command line. Parses CLI args, validates them and calls run(). 
The arguments dedicated to this framework are expected to precede the remaining args 
(for clarity of reading the entire command) but don't need to. In order to clearly
separate from the args required for the call being run, they are preceded by `--SF_*`.

There is a short form and long form of each command:
    
* `[--SF-s|--SF-data-source]` - The name of the data source being called. This is the
name of the plugin module being called. Required.
* `[--SF-g|--SF-data-source-group`] - The plugin group where the plugin lives. This is 
the plugins subdirectory where the plugin module is deployed. Required.
`[--SF-a|--SF-action]` - The plugin action being called. One of five supported actions that must be part of every plugin:

- `get_data` - retrieves available data for the keys passed to it
- `get_namespaced_data` - retrieves available data for the keys passed to it, with the attribute keys associated with each
key prepended with the plugin name and plugin group
- `adds_keys` - returns a JSON object with the attribute `adds_keys` and a 
boolean indicating whether the data source adds keys or just gets data for the keys passed to it
- `get_schema` - returns a JSON object with the attribute `schema` and the schema of attributes which 
this data source may add for each key
- `get_namespaced_schema` - returns a JSON object with the attribute `schema` and the schema of attributes which 
this data source may add for each key, with each attribute prepended with the plugin name and plugin group
- `parse_args` - returns the values parsed for the arguments passed to the call being 
made as a JSON object with an attribute `args` and an array of parsed args,
and an attribute `is_valid` with a boolean indicating whether parsing succeeded.

The `[--SF-a|--SF-action]` argument is Optional. If you don't pass it, `get_data` is assumed.  

Calls to `get_data` can be piped together. All the calls must be enclosed in quotes as shown 
in the examples below.  Calls to `adds_keys` and `get_schema` and `parse_args` cannot 
be piped. Only the first data-source and data-source group passed to the call with this 
action will be used to perform that action and return the result.

The complete interface for a call piping two get_data calls together:
    
    PATH/runner.py \'[--SF-s|--SF-data-source] DATA_SOURCE_1 \\
    [--SF-g|--SF-data-source-group] DATA_SOURCE_GROUP_1 \\
    ARGS | \\ 
    [--SF-s|--SF-data-source] DATA_SOURCE_2 \\
    [--SF-g|--SF-data-source-group] DATA_SOURCE_GROUP_2 \\
    ARGS\'

An example call piping two get_data calls together:
    
    PATH/runner.py \'--SF-s fidelity --SF-g examples \\
    -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL | \\
    --SF-s ystockquotelib --SF-g examples\'

An example get_schema call:
    
    PATH/runner.py \'--SF-s fidelity --SF-g examples --SF-a get_schema \\
    -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL\'
"""
   
    # If input passed from stdin, set initial data in chain of calls to that.
    # Thus supports composing sofine piped chains with preceding outer piped
    #  command line statements that include sofine pipes within them
    ret = {}
    if utils.has_stdin():
        ret = sys.stdin.read()
        ret = json.loads(ret)

    # Get each piped data source and set of args to call it from the CLI
    # CLI syntax is split on pipes
    calls = ' '.join(argv).split('|')
    for call in calls:
        call = call.strip()
        data_source, data_source_group, action, data_source_args = \
                _parse_runner_args(call.split())
        ret = _run_action(action, ret, data_source, data_source_group, data_source_args)

    print json.dumps(ret)


if __name__ == '__main__':
    # Client passes in a statement of one or more piped calls to
    #  data sources enclosed in quotes. Convert to list here because
    #  code in main() and run() expects an argument list
    argv = sys.argv[1]
    argv = argv.split()
    main(argv)

