#!/anaconda/bin/python -tt

import unittest
import sys
import subprocess
import inspect
sys.path.insert(0, '..')
import sofine.runner as runner


# Hack to fill in the sensitive values from the command line
path_to_runner = "FILL ME IN"
c = "FILL ME IN"
p = "FILL ME IN"
a = "FILL ME IN"
e = "FILL ME IN"
customer_id = "FILL_ME_IN"
password = "FILL_ME_IN"
account_id = "FILL_ME_IN"
email = "FILL_ME_IN"


class TestCase(unittest.TestCase):

    def test_runner_main_fidelity(self):
        # Need to restore zeroth argv arg (name of module) to the synthesized argv
        #  passed runner.py. Because when it is called directly of course it will
        #  have this argument
        # NOTE: Piped (and single non-piped) command lines need to enclose the 
        #  entire set of piped calls in quotes, which here are single quotes 
        cmd_get_data = "{0}/runner.py '-s fidelity {1} {2} {3} {4} {5} {6} {7} {8}'".format(
                path_to_runner, c, customer_id, p, password, a, account_id, e, email)
        # NOTE: This call failed with this error message: "sys.excepthook is missing.
        #  lost sys.stderr" until adding stderr arg to Popen() call
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = eval(out)
    
        self.assertTrue(len(out.keys()))


    def test_runner_main_fidelity_pipe_ystockquotelib(self):
        # NOTE: Piped (and single non-piped) command lines need to enclose the 
        #  entire set of piped calls in quotes, which here are single quotes 
        cmd_get_data = "{0}/runner.py '-s fidelity {1} {2} {3} {4} {5} {6} {7} {8}".format(
                path_to_runner, c, customer_id, p, password, a, account_id, e, email)
        cmd_get_data += "|"
        cmd_get_data += "-s ystockquotelib'"
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = eval(out)
        
        self.assertTrue(len(out.keys()))


# NOTE: This runs as unittest but requires extra args from the command line (to
#  not embed sensitive ids here or in config files etc.). So it's basically a manual
#  test with nice unittest output
# Sample call: ~/code/sofine markweiss$ ./tests/test_runner_from_cli.py \
#              ~/code/sofine/sofine \
#              -c MY_CUSTOMER_ID \
#              -p MY_PASSWORD \
#              -a MY_ACCOUNT_ID \
#              -e MY_EMAIL
if __name__ == '__main__':
    # Load the module scope variables from CLI args
    # This lets us not hard-code sensitive values needed for the test
    path_to_runner, c, customer_id, p, password, a, account_id, e, email = sys.argv[1:]
    # Now delete CLI args from argv because calling unittest.main() with
    #  argv args other than the module name in arg 0 causes unittest exception
    # This loop from last index to first index, not 0th, stepping down by 1
    # We want this because the we want to truncate all of sys.argv except for the first arg
    for i in range(len(sys.argv) - 1, 0, -1):
        del sys.argv[i]

    unittest.main()

