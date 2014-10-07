import unittest
import sys
import sofine.runner as runner
import sofine.lib.utils.utils as utils


class TestCase(unittest.TestCase):
    
    def test_runner_mock_http_plugin(self):
        data = {"AAPL" : [], "MSFT" : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock_http'
        data_source_args = []
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        actual_keys = set(data.keys())
        expected_keys = set(['AAPL', 'MSFT'])

        self.assertTrue(expected_keys == actual_keys)
        for k in actual_keys:
            self.assertTrue(len(data[k]))
            for attr in data[k]:
                for k,v in attr.iteritems():
                    self.assertTrue(k is not None and v is not None)


    def test_runner_mock_namespaced_http_plugin(self):
        data = {"AAPL" : [], "MSFT" : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock_http'
        data_source_args = []
        data = runner.get_namespaced_data(data, data_source, data_source_group, data_source_args)
        
        actual_keys = set(data.keys())
        expected_keys = set(['AAPL', 'MSFT'])

        self.assertTrue(expected_keys == actual_keys)
        for k in actual_keys:
            self.assertTrue(len(data[k]))
            for attr in data[k]:
                for k,v in attr.iteritems():
                    self.assertTrue(k is not None and k.startswith('mock_http::ystockquotelib_mock::') and v is not None)
   

        data = {'AAPL' : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock_http'
        args = []
        data = runner.get_data(data, data_source, data_source_group, args)
        schema = runner.get_schema(data_source, data_source_group)
        attr_keys = [attr.keys()[0] for attr in data['AAPL']]
        self.assertTrue(set(attr_keys) == set(schema['schema']))


if __name__ == '__main__':  
    unittest.main()
