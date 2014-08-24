import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner
import sofine.lib.utils.utils as utils

class TestCase(unittest.TestCase):
    
    def test_runner_get_data_ystockquote(self):
        key = 'AAPL'
        data = {key : []}
        data_source = 'ystockquotelib'
        data_source_group = 'example'
        data_source_args = []
        
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : [], key2 : []}
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])
    
    
    def test_runner_get_data_archive_dot_org(self):
        key = 'AAPL'
        data = {key : []}
        data_source = 'archive_dot_org_search_results'
        data_source_group = 'example'
        data_source_args = []
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : [], key2 : []}
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])


    def test_runner_get_data_google_search_results(self):
        key = 'AAPL'
        data = {key : []}
        data_source = 'google_search_results'
        data_source_group = 'example'
        data_source_args = []
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : [], key2 : []}
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])
    
    
    def test_schema_ystockquote(self):
        key = 'AAPL'
        data = {key : []}
        data_source = 'ystockquotelib'
        data_source_group = 'example'
        data_source_args = []
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        expected_attributes = runner.get_schema(data_source, data_source_group)
        # Set intersection of actual keys and expected keys must have at least
        #  one element. ystockquotelib doesn't guarantee returning all keys
        #  found in schema as attribute keys for every key passed to it,
        #  but it does guarantee those keys will be a subset of the keys in schema.
        data_keys = utils.get_attr_keys(data)
        self.assertTrue(set(data_keys) & set(expected_attributes['schema']))


    def test_runner_get_data_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib']
        data_source_groups = ['standard', 'example']
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        file_source_args = ['-p', path]
        ystockquote_args = []
        data_source_args = [file_source_args, ystockquote_args]
        
        data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))
        self.assertTrue(len(data['AAPL']) and len(data['MSFT'])) 


    # Test composing operations where some are an initial source of keys, some
    #  add new keys in an intermediate step, and some just add attributes to keys
    # ==> The end result of the pipeline is the union of each step.
    def test_runner_pipeline(self):
        data = {}
        data_sources = ['file_source', 'file_source', 'ystockquotelib']
        data_source_groups = ['standard', 'standard', 'example']
        
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        file_source_args_1 = ['-p', path]
        path_2 = './sofine/tests/fixtures/file_source_test_data_2.txt'
        file_source_args_2 = ['-p', path_2]
        ystockquote_args = []
        
        data_source_args = [file_source_args_1, file_source_args_2, ystockquote_args]
        data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

        # Assert that final output has keys from each file_source step
        file_source_keys_1 = runner.get_schema('file_source', 'standard', file_source_args_1)
        file_source_keys_2 = runner.get_schema('file_source', 'standard', file_source_args_2)
        for k in file_source_keys_1['schema']:
            self.assertTrue(k in data)
        for k in file_source_keys_2['schema']:
            self.assertTrue(k in data)
        # Assert that the final output has values from ystockquotelib for 
        #  keys added by file_source
        for k in file_source_keys_1['schema']:
            self.assertTrue(len(data[k].keys()))
        for k in file_source_keys_2['schema']:
            self.assertTrue(len(data[k].keys()))


if __name__ == '__main__':  
    unittest.main()

