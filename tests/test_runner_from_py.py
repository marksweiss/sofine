#!/anaconda/bin/python -tt

import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner

class TestCase(unittest.TestCase):
    
    def test_runner_run_ystockquote(self):
        key = 'AAPL'
        data = {key : {}}
        data_source = 'ystockquotelib'
        data_source_group = 'example'
        data_source_args = []
        data = runner.run(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : {}, key2 : {}}
        data = runner.run(data, data_source, data_source_group, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])


    def test_schema_ystockquote(self):
        key = 'AAPL'
        data = {key : {}}
        data_source = 'ystockquotelib'
        data_source_group = 'example'
        data_source_args = []
        data = runner.run(data, data_source, data_source_group, data_source_args)
        
        expected_attributes = runner.get_schema(data_source, data_source_group)
        # Set intersection of actual keys and expected keys must have at least
        #  one element. ystockquotelib doesn't guarantee returning all keys
        #  found in schema as attribute keys for every key passed to it,
        #  but it does guarantee those keys will be a subset of the keys in schema.
        self.assertTrue(set(data[key].keys()) & set(expected_attributes))


    def test_runner_file_source(self):
        data = {}
        data_source = 'file_source'
        data_source_group = 'standard'
        # This path needs to match the path relative to file_source.py
        #  where the code using the path variable to find the test data file runs
        path = './tests/fixtures/file_source_test_data.txt'
        data_source_args = ['-p', path]
        data = runner.run(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))


    def test_schema_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual_keys = runner.get_schema(data_source, data_source_group, args)
        
        expected_keys = set(['AAPL', 'MSFT'])
        
        self.assertTrue(expected_keys == set(actual_keys))


    def test_runner_run_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib']
        data_source_groups = ['standard', 'example']
        path = './tests/fixtures/file_source_test_data.txt'
        file_source_args = ['-p', path]
        ystockquote_args = []
        data_source_args = [file_source_args, ystockquote_args]
        
        data = runner.run_batch(data, data_sources, data_source_groups, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))
        self.assertTrue(len(data['AAPL']) and len(data['MSFT'])) 


    # Test composing operations where some are an initial source of keys, some
    #  add new keys in an intermediate step, and some just add attributes to keys
    # ==> The end result of the pipeline is the union of each step.
    def test_runner_pipeline(self):
        data = {}
        data_sources = ['file_source', 'file_source', 'ystockquotelib']
        data_source_groups = ['standard', 'standard', 'example']
        
        path = './tests/fixtures/file_source_test_data.txt'
        file_source_args_1 = ['-p', path]
        path_2 = './tests/fixtures/file_source_test_data_2.txt'
        file_source_args_2 = ['-p', path_2]
        ystockquote_args = []
        
        data_source_args = [file_source_args_1, file_source_args_2, ystockquote_args]
        data = runner.run_batch(data, data_sources, data_source_groups, data_source_args)

        # Assert that final output has keys from each file_source step
        file_source_keys_1 = runner.get_schema('file_source', 'standard', file_source_args_1)
        file_source_keys_2 = runner.get_schema('file_source', 'standard', file_source_args_2)
        for k in file_source_keys_1:
            self.assertTrue(k in data)
        for k in file_source_keys_2:
            self.assertTrue(k in data)
        # Assert that the final output has values from ystockquotelib for 
        #  keys added by file_source
        for k in file_source_keys_1:
            self.assertTrue(len(data[k].keys()))
        for k in file_source_keys_2:
            self.assertTrue(len(data[k].keys()))


if __name__ == '__main__':  
    unittest.main()

