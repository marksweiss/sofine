import os
import unittest
import sys
import subprocess
import inspect
import json
import csv
import sofine.runner as runner
import sofine.lib.utils.utils as utils


class RunnerFromCliHttpPluginTestCase(unittest.TestCase):

    def test_runner_main_http_plugin(self):
        cmd_get_data = "echo '{\"AAPL\" : []}'"
        cmd_get_data += " | "
        cmd_get_data += "python ./sofine/runner.py '--SF-s google_search_results --SF-g example_http'"
        
        
        # TEMP DEBUG
        print cmd_get_data
        
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(out.keys() == ['AAPL'])
       

        # TEMP DEBUG
        print out


        for k in out.keys():
            attr_keys = [attr.keys()[0] for attr in out[k]]
            self.assertTrue(len(attr_keys))
            for attr in out[k]:    
                self.assertTrue(attr.keys() and len(attr.keys()) and attr.keys()[0] is not None and \
                        attr.values() and len(attr.values()) and attr.values()[0] is not None)


#    def test_runner_main_namespaced_http_plugin(self):
#        cmd_get_namespaced_data = "echo '{\"AAPL\" : [], \"MSFT\" : []}'"
#        cmd_get_namespaced_data += " | "
#        cmd_get_namespaced_data += "python ./sofine/runner.py '--SF-s google_search_results --SF-g example_http --SF-a get_namespaced_data'"
#        proc = subprocess.Popen(cmd_get_namespaced_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        out = proc.stdout.read()
#        out = json.loads(out)
#
#
#        # TEMP DEBUG
#        print out
#
#
#        self.assertTrue(len(out.keys()) == 2)
#        self.assertTrue(set(out.keys()) == set(['AAPL', 'MSFT']))
#        
#        for k in out.keys():
#            self.assertTrue(len(out[k]))
#            for attr in out[k]:
#                for k,v in attr.iteritems():
#                    self.assertTrue(k is not None and k.startswith('example_http::google_search_results::') and v is not None)
#    




if __name__ == '__main__':
    unittest.main()

