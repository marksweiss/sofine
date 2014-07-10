#!/anaconda/bin/python -tt

import lib.utils.utils as utils 
from optparse import OptionParser
import json
import sys


def run(data, data_source, data_source_group, data_source_args):
    """Main driver function. Takes a list of data_sources and a list of argument lists to call when 
calling each data_source. Can be called directly or from main if this module was instantiated from the 
command line."""
    mod = utils.load_module(data_source, data_source_group)
    is_valid, parsed_args = mod.parse_args(data_source_args)
    if not is_valid:
        raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))

    new_data = mod.get_data(data, parsed_args)
    # Here are the core data aggregation semantics:
    #  - if this is the first call in the chain, data is empty, so just fill it with the return of this call
    #  - if there is already data, add attribute key/value pairs associated with any existing keys, 
    #    so call update() on the value mapped to each key, which is a dict of attribute/values
    #  - if there is already data, add any new keys discovered by this call to get_data as keys with new
    #    empty attribute dicts
    # So, the set of keys on each call is the union of all previously collected keys
    # So, the set o attributes associated with each key is the union of all previously collected attribute/value
    #  pairs collected for that key
    if data:
        for k in data.keys():
            data[k].update(new_data[k])
        new_keys = set(new_data.keys()) - set(data.keys())
        new_key_attrs = dict.fromkeys(new_keys, {})
        data.update(new_key_attrs)
    else:
        data = new_data
    
    return data


def run_batch(data, data_sources, data_source_groups, data_source_args):
    if len(data_sources) != len(data_source_args) or \
            len(data_sources) != len(data_source_groups) or \
            len(data_source_groups) != len(data_source_args):
        raise ValueError("""Call to runner.batch_run() had different lengths for 
data_sources (len == {0}), 
data source_groups (len == {1}) and 
data_source_args (len == {2)}""".format(len(data_sources), len(data_source_groups), len(data_source_args)))
    
    for j in range(0, len(data_sources)):
        data = run(data, data_sources[j], data_source_groups[j], data_source_args[j])

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
        mod = utils.load_module(data_source, data_source_group)
        is_valid, parsed_args = mod.parse_args(args)
        if not is_valid:
            raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))
        schema = mod.get_schema(parsed_args)
    
    return schema


def main(argv):
    """Entry point if called from the command line. Parses CLI args, validates them and calls run(). 
The interface for call is as follows:
    PATH/runner.py '-s DATA_SOURCE_1 -g DATA_SOURCE_GROUP_1 ARGS | -s DATA_SOURCE_2 -g DATA_SOURCE_GROUP_2 ARGS'
Example:
    PATH/runner.py '-s fidelity -g examples -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL | -s ystockquotelib -g examples'
"""
    def parse_runner_args(args):
        data_source = None
        data_source_group = None
        data_source_args = []
        
        def parse_runner_arg(args, arg_flag):
            i = -1
            try:
                i = args.index(arg_flag)
            except ValueError:
                raise ValueError('Required argument {0} not found in command line argument list passed to runner.main()'.format(arg_flag))
            if i == len(args) - 1:
                raise ValueError ('Value for required argument {0} not found in command line argument list passed to runner.main()'.format(arg_flag))
            ret = args[i + 1]
            del args[i + 1]
            del args[i]
            
            return ret
        
        data_source = parse_runner_arg(args, '-s')
        data_source_group = parse_runner_arg(args, '-g')

        return data_source, data_source_group, args
    
    data = {}
    # Get each piped data source and set of args to call it from the CLI
    # CLI syntax is split on pipes
    calls = ' '.join(argv).split('|')
    for call in calls:
        call = call.strip()
        data_source, data_source_group, data_source_args = parse_runner_args(call.split())
        data = run(data, data_source, data_source_group, data_source_args)

    print json.dumps(data)


if __name__ == '__main__':
    # Client passes in a statement of one or more piped calls to
    #  data sources enclosed in quotes. Convert to list here because
    #  code in main() and run() expects an argument list
    argv = sys.argv[1]
    argv = argv.split()
    main(argv)

