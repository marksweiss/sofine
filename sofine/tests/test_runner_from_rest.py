import unittest
import sys
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
        data_source = 'archive_dot_org_search_results'
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


    def test_rest_runner_pipeline(self):
        post_data = {"AAPL" : {}, "MSFT" : {}}
        data_source_1 = 'google_search_results' # 'ystockquotelib' 
        data_source_group_1 = 'example'
        data_source_2 = 'archive_dot_org_search_results'
        data_source_group_2 = 'example'

        url = 'http://localhost:{0}/SF-s/{1}/SF-g/{2}/SF-s/{3}/SF-g/{4}'.format(
                conf.REST_PORT, 
                data_source_1, data_source_group_1,
                data_source_2, data_source_group_2)
        ret = urllib2.urlopen(url, json.dumps(post_data))
        ret = ret.read()
        ret = json.loads(ret)

        # The keys returned match and there are attributes from the call for each key
        self.assertTrue(set(ret.keys()) == set(post_data.keys()))
        for k in ret.keys():
            self.assertTrue(ret[k].keys())

        url = 'http://localhost:{0}/SF-s/{1}/SF-g/{2}/SF-a/get_schema'.format(
                conf.REST_PORT, data_source_1, data_source_group_1)

        schema_1 = urllib2.urlopen(url)
        schema_1 = schema_1.read()
        schema_1 = json.loads(schema_1)
        
        url = 'http://localhost:{0}/SF-s/{1}/SF-g/{2}/SF-a/get_schema'.format(
                conf.REST_PORT, data_source_2, data_source_group_2)
        schema_2 = urllib2.urlopen(url)
        schema_2 = schema_2.read()
        schema_2 = json.loads(schema_2)
        
        # Make a set of all the attribute keys found in the return data
        all_data_attrs = set()
        for k in ret.keys():
            for attr_key in ret[k]:
                all_data_attrs.add(attr_key)

        for k in schema_1['schema']:
            self.assertTrue(k in all_data_attrs)
        for k in schema_2['schema']:
            self.assertTrue(k in all_data_attrs)


if __name__ == '__main__':  
    unittest.main()

