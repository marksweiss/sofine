#!/anaconda/bin/python -tt

import lib.utils.utils as utils 
from optparse import OptionParser
import sys
import json


def run(data, data_source, data_source_args):
    """Main driver function. Takes a list of data_sources and a list of argument lists to call when 
calling each data_source. Can be called directly or from main if this module was instantiated from the 
command line."""
    mod = utils.load_module(data_source)

    is_valid, parsed_args = mod.parse_args(data_source_args)
    if not is_valid:
        raise ValueError ('Invalid value passed in call to {0}. Args passed: {1})'.format(data_source, data_source_args))

    new_data = mod.get_data(data, parsed_args)
    # Here are the core data aggregation semantics:
    #  - if this is the first call in the chain, data is empty, so just fill it with the return of this call
    #  - if there is already data, the first call in the chain set the set of keys we care about, and each
    #    call that follows can add attribute key/value pairs associated with that key, so call update() on the
    #    value mapped to each key, which is a dict of attribute/values
    if data:
        for k in data.keys():
            data[k].update(new_data[k])
    else:
        data = new_data
    
    return data


# TODO UNIT TEST THIS
def run_batch(data, data_sources, data_source_args):
    if len(data_sources) != len(data_source_args):
        raise ValueError('Call to runner.batch_run() had {0} data sources and {1} data_source_args'.format(len(data_sources), len(data_source_args)))
    
    for j, data_source in enumerate(data_sources):
        data = _run(data, data_source[j], data_source_args[j])

    return data


def get_schema(data_source):
"""Return the schema fields for a data source. This is the set of keys in the
attribute dict mapped to each key in data. Not all data sources gurarantee they will
return all attribute keys for each key in data, and not all data sources guarantee
they will return the same set of attribute keys for each key in data in one returned
data set."""
    mod = utils.load_module(data_source)
    schema = mod.get_schema()
    return schema

def main(argv):
    """Entry point if called from the command line. Parses CLI args, validates them and calls run(). 
The interface for call is as follows:
    PATH/runner.py '-s DATA_SOURCE_1 ARGS | -s DATA_SOURCE_2 ARGS'
Example:
    PATH/runner.py '-s fidelity -c CUSTOMER_ID -p PASSWORD -a ACCOUNT_ID -e EMAIL | -s ystockquotelib'
"""
    def parse_data_source(args):
        i = -1
        data_source = None
        data_source_args = []
        try:
            i = args.index('-s')
        except ValueError:
            raise ValueError('Required argument "-s" not found in command line argument list passed to runner.main()')
        if i == len(args) - 1:
            raise ValueError ('Value for required argument "-s" not found in command line argument list passed to runner.main()')
        else:
            # Get the data source value from the position after it's argument
            data_source = args[i + 1]
            # Now remove data source arg and value from the list. The rest of the argv list are the args
            #  to pass to the call to the data source
            del args[i + 1]
            del args[i]

        return data_source, args
    
    data = {}
    # Get each piped data source and set of args to call it from the CLI
    # CLI syntax is split on pipes
    calls = ' '.join(argv).split('|')
    for call in calls:
        call = call.strip()
        data_source, data_source_args = parse_data_source(call.split())
        data = run(data, data_source, data_source_args)

    print json.dumps(data)


if __name__ == '__main__':
    # Client passes in a statement of one or more piped calls to
    #  data sources enclosed in quotes. Convert to list here because
    #  code in main() and run() expects an argument list
    argv = sys.argv[1]
    argv = argv.split()
    main(argv)

