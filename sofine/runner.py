#!/anaconda/bin/python -tt

import lib.utils.utils as utils 
from optparse import OptionParser
import sys


def main(*argv):
    """Entry point if called from the command line. Parses CLI args, validates them and calls run()."""    
    data = None
    data_sources = None
    data_source_args = None
    # Test for stdin. If it's the first call in the chain there won't be data
    #  from stdin and instead the command line arg must be an empty dict. This calling
    #  mode is also useful for testing. If there is stdin then this is one in a chain
    #  of piped data source calls, so data == stdin.
    has_stdin_data = not sys.stdin.isatty()
    if has_stdin_data:
        data = sys.stdin.read() 
        # If data is coming on stdin, we only have two args, data_sources and data_source_args
        data_sources, data_source_args = argv
    else:
        data, data_sources, data_source_args = argv
    
    # Test that the runner args are valid
    is_valid = _validate_args(data, data_sources, data_source_args)

    
    # TODO THIS NEEDS TO COMPOSE AND REPLACE all the validated data_source_args
    #  and then call run() once with the list of data_sources and args
    #  since run handles the logic of looping and composing the result.
    # NOTE THIS BLOCK IS WRONG

    if is_valid:
        # Now test that the args for each data source passed in can be parsed
        #  validly from their CLI argv form into a list of args for that module's get_data(0 call
        for j, args in enumerate(data_source_args):
            parsed_data_source_args = []
            
            # TEMP DEBUG
            print data_sources[j]
            
            mod = utils.load_module(data_sources[j])
            
            # TEMP DEBUG
            print mod
            
            # Test the args. Get them returned parsed into a list of the arg values.
            # This is what we pass to mod.get_data() for this module.
            # So if the args are valid, put the returned list into that in data_source_args
            is_valid, parsed_args = mod.parse_args(data_source_args[j])
            if is_valid:
               parsed_data_source_args.append(parsed_args) 
            else:
                # TODO Raise exception here
                # If any of the provided data source calls has invalid args, the entire
                #  operation exits without running any of the calls
                print ''
                return None
        
        validate_args = False
        data = run(data, data_sources, parsed_data_source_args, validate_args)
        
        # CLI callee returns output to stdout, not in a Py variable
        # The semantics of calling this are to call one or piped data sources
        print data
        return
    else:
        # TODO Raise exception here
        print ''
        return

if __name__ == '__main__':
    data = {}
    sys.exit(main(data, sys.argv[1:]))


def run(data, data_sources, data_source_args, validate_args=True):
    """Main driver function. Takes a list of data_sources and a list of argument lists to call when 
calling each data_source. Can be called directly, in which case the caller is strongly advised
to omit the validate_args argument or pass in True for it. Can be called from main if this
module was instantiated from the command line, in which case main() will have parsed and
validated the arguments already, so it calls run() with validate_args = False."""
    is_valid = True
    if validate_args:
        is_valid = _validate_args(data, data_sources, data_source_args)

    if is_valid:
        # This is actually the two lines that do all the work in the module
        # calling each data source with its args and adding whatever it gets
        # to a dict which then gets returned
        for j, data_source in enumerate(data_sources):
            mod = utils.load_module(data_source)
            if is_valid:
                mod.get_data(data, data_source_args[j])
    else:
        pass
        # TODO Raise exception here

    return data


usage = """[-d|--data-sources] - [String] List of data source modules from which to retrieve data. Required.
[-a|--data-source-args] - [[]] List of lists of args for calling each data source. Order and length of list must match 'data_sources'. Required."""

def get_args_dict():
    return {'data_sources' : ''}

def help():
    print usage


def parse_args(argv):
    parser = OptionParser(usage=usage)

    # TEMP DEBUG
    print argv

    parser.add_option("-d", "--data", 
                      action="store", dest="data",
                      help="""Serialized dict (i.e. JSON string) that is empty or has string keys mapped to 
empty dicts or non-empty dicts with string fields mapped to values of any type. Required.""") 
    
    parser.add_option("-s", "--data-sources", 
                      action="store", dest="data_sources",
                      help="List of data source modules from which to retrieve data. Required.") 

    parser.add_option("-a", "--data-source-args", 
                      action="store", dest="data_source_args",
                      help="List of lists of args for calling each data source. Order and length of list must match 'data_sources'. Required.") 
    
    (opts, args) = parser.parse_args(argv)
   
    if not opts.data_sources:
        print "Invalid argument error."
        print """
Your args:
  data {0}
  data_sources {1}
  data_source_args {2}""".format(opts.data, opts.data_sources, opts.data_source_args)
        print usage
        is_valid = False
    
    return is_valid, opts.data, opts.data_sources, opts.data_source_args


def _validate_args(data, data_sources, data_source_args):
    """Additional argument validation. Validates that:
- 'data' is a dict
- at least one non-empty string 'data_source' is provided
- at least one empty or non-empty list of 'data_source_args' is provided
- number of 'data_sources' matches the number of data_source_args."""
    if not type(data) is dict:
        return False
    if len(data_sources) == 0 or len(data_source_args) == 0:
        return False
    for source in data_sources:
        if not source:
            return False
    for arg in data_source_args:
        if not type(arg) is list:
            return False
    if len(data_sources) != len(data_source_args):
        return False
    return True

