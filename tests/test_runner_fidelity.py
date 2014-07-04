#!/anaconda/bin/python -tt

import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner


# Must be called manually from the command line, because it passes
#  confidential args to fidelity
def main(argv):
    data = {}
    data_sources = ['fidelity']
    # NOTE: This command line must suppy the args expected by sofine.lib.fidelity.parse_args()
    # Also, passed as a list of args since that is the runner interface
    data_source_args = [argv]
    
    return runner.main([data, data_sources, data_source_args])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

