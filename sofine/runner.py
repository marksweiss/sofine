import lib.utils.utils as utils
import lib.utils.conf as conf
from optparse import OptionParser
import json
import sys


def get_data(data, data_source, data_source_group, data_source_args):
    """Main driver function. Takes a list of data_sources and a list of argument lists to call when 
calling each data_source. Can be called directly or from main if this module was instantiated from the 
command line."""
    mod = utils.load_module(data_source, data_source_group)
    is_valid, parsed_args = mod.parse_args(data_source_args)
    if not is_valid:
        raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))

    new_data = mod.get_data(data.keys(), parsed_args)
    
    # Here are the core data aggregation semantics:
    #  - if this is the first call in the chain, data is empty, so just fill it with the return of this call
    #  - if there is already data, add attribute key/value pairs associated with any existing keys, 
    #    so call update() on the value mapped to each key, which is a dict of attribute/values
    #  - if there is already data, add any new keys discovered by this call to get_data as keys with new
    #    empty attribute dicts
    # So, the set of keys on each call is the union of all previously collected keys
    # So, the set o attributes associated with each key is the union of all previously collected attribute/value
    #  pairs collected for that key
    if len(new_data.keys()) > 0:
        for k in new_data.keys():
            if k in data:
                data[k].update(new_data[k])
            else:
                data[k] = new_data[k]
    
    return data


def get_data_batch(data, data_sources, data_source_groups, data_source_args):
    if len(data_sources) != len(data_source_args) or \
            len(data_sources) != len(data_source_groups) or \
            len(data_source_groups) != len(data_source_args):
        raise ValueError("""Call to runner.batch_run() had different lengths for 
data_sources (len == {0}), 
data source_groups (len == {1}) and 
data_source_args (len == {2)}""".format(len(data_sources), len(data_source_groups), len(data_source_args)))
    
    for j in range(0, len(data_sources)):
        data = get_data(data, data_sources[j], data_source_groups[j], data_source_args[j])

    return data


def get_schema(data_source, data_source_group, args=None):
    """Return the schema fields for a data source. This is the set of keys in the
attribute dict mapped to each key in data. Not all data sources gurarantee they will
return all attribute keys for each key in data, and not all data sources guarantee
they will return the same set of attribute keys for each key in data in one returned
data set."""
    mod = utils.load_module(data_source, data_source_group)
    schema = None
    if not args:
        schema = mod.get_schema()
    else:
        is_valid, parsed_args = mod.parse_args(args)
        if not is_valid:
            raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))
        schema = mod.get_schema(parsed_args)
   
    return {"schema" : schema} 


def adds_keys(data_source, data_source_group):
    mod = utils.load_module(data_source, data_source_group)
    adds_keys = mod.adds_keys()
    return {"adds_keys" : adds_keys}


def parse_args(data_source, data_source_group, data_source_args):
    mod = utils.load_module(data_source, data_source_group)
    is_valid, parsed_args = mod.parse_args(data_source_args)
    return {"is_valid" : is_valid, "parsed_args" : parsed_args}
    

def main(argv):
    """Entry point if called from the command line. Parses CLI args, validates them and calls run(). 
The arguments dedicated to this framework are expected to precede the remaining args 
(for clarity of reading the entire command) but don't need to. In order to clearly
separate from the args required for the call being run, they are preceded by '--SF_*'.

There is a short form and long form of each command:
    [--SF-s|--SF-data-source] - The name of the data source being called. This is the 
        name of the plugin module being called. Required.
    [--SF-g|--SF-data-source-group] - The plugin group where the plugin lives. This is 
        the plugins subdirectory where the plugin module is deployed. Required.
    [--SF-a|--SF-action] - The plugin action being called. One of four supported actions
        that must be part of every plugin:
            - 'get_data' - retrieves available data for the keys passed to it
            - 'adds_keys' - returns a JSON object with the attribute 'adds_keys' and a 
                boolean indicating whether the data source adds keys or just gets data 
                for the keys passed to it
            - 'get_schema' - returns a JSON object with the attribute 'schema' and the 
                schema of attributes which this data source may add for each key
            - 'parse_args' - returns the values parsed for the arguments passed to the call being 
                made as a JSON object with an attribute 'args' and an array of parsed args,
                and an attribute 'is_valid' with a boolean indicating whether parsing succeeded.
    The '--SF-a|--SF-action' argument is Optional. If you don't pass it, 'get_data' is assumed.  

Calls to 'get_data' can be piped together. All the calls must be enclosed in quotes as shown 
in the examples below.  Calls to 'adds_keys' and 'get_schema' and 'parse_args' cannot 
be piped. Only the first data-source and data-source group passed to the call with this 
action will be used to perform that action and return the result.

The complete interface for a call piping two get_data calls together:
    PATH/runner.py '[--SF-s|--SF-data-source] DATA_SOURCE_1 \
                    [--SF-g|--SF-data-source-group] DATA_SOURCE_GROUP_1 \
                    ARGS | \ 
                    [--SF-s|--SF-data-source] DATA_SOURCE_2 \
                    [--SF-g|--SF-data-source-group] DATA_SOURCE_GROUP_2 \
                    ARGS'

An example call piping two get_data calls together:
    PATH/runner.py '--SF-s fidelity --SF-g examples \
                    -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL | \
                    --SF-s ystockquotelib --SF-g examples'

An example get_schema call:
    PATH/runner.py '--SF-s fidelity --SF-g examples --SF-a get_schema \
                    -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL'

"""
    def parse_runner_args(args):
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
                parse_runner_args(call.split())

        if action == 'get_data':
            ret = get_data(ret, data_source, data_source_group, data_source_args)
        # Only get_data() supports chaining, so just break after one of other actions
        elif action == 'get_schema':
            ret = get_schema(data_source, data_source_group, data_source_args)
            break
        elif action == 'adds_keys':
            ret = adds_keys(data_source, data_source_group)
            break
        elif action == 'parse_args':
            ret = parse_args(data_source, data_source_group, data_source_args)
            break

    print json.dumps(ret)


if __name__ == '__main__':
    # Client passes in a statement of one or more piped calls to
    #  data sources enclosed in quotes. Convert to list here because
    #  code in main() and run() expects an argument list
    argv = sys.argv[1]
    argv = argv.split()
    main(argv)

