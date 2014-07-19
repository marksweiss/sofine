import unittest
import sys
sys.path.insert(0, '..')
import sofine.rest_runner as rest_runner
import sofine.lib.utils.conf as conf
import urllib2
import json
import multiprocessing


class TestCase(unittest.TestCase):
   
    def setUp(self):
        from wsgiref.simple_server import make_server
        server = make_server('localhost', conf.REST_PORT, rest_runner.application)
        self.server_process = multiprocessing.Process(target=server.serve_forever)
        self.server_process.start()


    def tearDown(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)


    def test_rest_runner(self):
        post_data = {"AAPL" : {}, "MSFT" : {}}
        data_source = 'ystockquotelib'
        data_source_group = 'example'
        
        url = 'http://localhost:{0}/SF-s/{1}/SF-g/{2}'.format(
                conf.REST_PORT, data_source, data_source_group)
        ret = urllib2.urlopen(url, json.dumps(post_data))
        ret = ret.read()
        ret = json.loads(ret)

        # The keys returned match and there are attributes from the call for each key
        self.assertTrue(set(ret.keys()) == set(['AAPL', 'MSFT']))
        for k in ret.keys():
            self.assertTrue(ret[k].keys())


if __name__ == '__main__':  
    unittest.main()

