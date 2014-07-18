import unittest
import sys
sys.path.insert(0, '..')
import sofine.rest_runner as rest_runner
import urllib2
import json
import cgitb
cgitb.enable()


class TestCase(unittest.TestCase):
    
    def test_runner_file_source(self):
        rest_runner.make_test_rest_runner()
        
        post_data = {}
        data_source = 'file_source'
        data_source_group = 'standard'
        path_arg = '-p'
        path = './tests/fixtures/file_source_test_data.txt'
        
        url = 'http://localhost:{0}?FS-s={1}&FS-g={2}&{3}={3}'.format(
                conf.REST_PORT, data_source, data_source_group, path_arg, path)
        url_ret = urllib2.urlopen(url, post_data)
        url_ret = url_ret.read()
        url_ret = json.loads(url_ret)

        self.assertTrue(set(url_ret.keys()) == set(['AAPL', 'MSFT']))


if __name__ == '__main__':  
    unittest.main()
