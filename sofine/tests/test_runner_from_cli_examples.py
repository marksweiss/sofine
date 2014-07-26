import unittest
import sys
import subprocess
import inspect
import json
sys.path.insert(0, '..')
import sofine.runner as runner


# Hack to fill in the sensitive values from the command line
c = "FILL ME IN"
p = "FILL ME IN"
a = "FILL ME IN"
e = "FILL ME IN"
customer_id = "FILL_ME_IN"
password = "FILL_ME_IN"
account_id = "FILL_ME_IN"
email = "FILL_ME_IN"

class RunnerFromCliExamplesTestCase(unittest.TestCase):
    
    def test_runner_main_fidelity(self):
        # NOTE: Piped (and single non-piped) command lines need to enclose the 
        #  entire set of piped calls in quotes, which here are single quotes 
        cmd_get_data = "python ./sofine/runner.py '--SF-s fidelity --SF-g example {0} {1} {2} {3} {4} {5} {6} {7}'".format(
                c, customer_id, p, password, a, account_id, e, email)
        # NOTE: This call failed with this error message: "sys.excepthook is missing.
        #  lost sys.stderr" until adding stderr arg to Popen() call
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
    
        self.assertTrue(len(out.keys()))


    def test_runner_main_fidelity_pipe_ystockquotelib(self):
        cmd_get_data = "python ./sofine/runner.py '--SF-s fidelity --SF-g example {0} {1} {2} {3} {4} {5} {6} {7}".format(
                c, customer_id, p, password, a, account_id, e, email)
        cmd_get_data += "|"
        cmd_get_data += "--SF-s ystockquotelib --SF-g example'"
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(len(out.keys()))


    def test_runner_main_pipeline(self):
        cmd_get_data = "python ./sofine/runner.py '--SF-s fidelity --SF-g example {0} {1} {2} {3} {4} {5} {6} {7}".format(
                c, customer_id, p, password, a, account_id, e, email)
        cmd_get_data += "|"
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        cmd_get_data += "--SF-s file_source --SF-g standard -p {0}".format(path)
        cmd_get_data += "|"
        cmd_get_data += "--SF-s ystockquotelib --SF-g example'"
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
       
        # Assert from fidelity is there for at least some of the keys
        # Note that there won't be fidelity data for the keys added by the file_source
        #  and that adds two keys, so we test that we have n-2 keys with fidelity schema fields
        count = 0
        expected = runner.get_schema('fidelity', 'example')
        for key in out.keys():
            if set(out[key].keys()) & set(expected['schema']):
                count += 1
        self.assertTrue(count == len(out.keys()) - 2)

        # Assert keys and data from keys added by file_source and retrieved by ystockquotelib are there
        file_source_args = ['-p', path]
        file_source_keys = runner.get_schema('file_source', 'standard', file_source_args)
        for k in file_source_keys['schema']:
            self.assertTrue(k in out)
        for k in file_source_keys['schema']:
            self.assertTrue(len(out[k].keys()))


# NOTE: This runs as unittest but requires extra args from the command line (to
#  not embed sensitive ids here or in config files etc.). So it's basically a manual
#  test with nice unittest output
# Sample call: PROJECT_ROOT$ python ./tests/test_runner_from_cli_examples.py \
#              -c MY_CUSTOMER_ID \
#              -p MY_PASSWORD \
#              -a MY_ACCOUNT_ID \
#              -e MY_EMAIL
if __name__ == '__main__':
    # Load the module scope variables from CLI args
    # This lets us not hard-code sensitive values needed for the test
    c, customer_id, p, password, a, account_id, e, email = sys.argv[1:]
    # Now delete CLI args from argv because calling unittest.main() with
    #  argv args other than the module name in arg 0 causes unittest exception
    # This loop from last index to first index, not 0th, stepping down by 1
    # We want this because the we want to truncate all of sys.argv except for the first arg
    for i in range(len(sys.argv) - 1, 0, -1):
        del sys.argv[i]

    unittest.main()
