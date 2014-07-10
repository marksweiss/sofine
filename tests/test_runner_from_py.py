#!/anaconda/bin/python -tt

import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner

class TestCase(unittest.TestCase):
    
    # Just here in case you want to skip this one while running others manually
    # @unittest.skip('')
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


    # Just here in case you want to skip this one while running others manually
    # @unittest.skip('')
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

    
    @unittest.skip("MUST RUN MANUALLY. ARGS INCLUDE SENSITIVE INFORMATION.")
    # LAST RUN: Jul 8 2014
    def test_runner_run_fidelity(self):
        data = {}
        data_source = 'fidelity'
        data_source_group = 'example'
        customer_id = "FILL_ME_IN"
        password = "FILL_ME_IN"
        account_id = "FILL_ME_IN"
        email = "FILL_ME_IN"
        data_source_args = ['-c', customer_id, '-p', password, '-a', account_id, '-e', email]
        data = runner.run(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(len(data.keys())) 

    
    @unittest.skip("MUST RUN MANUALLY. ARGS INCLUDE SENSITIVE INFORMATION.")
    # LAST RUN: Jul 8 2014
    def test_runner_run_batch(self):
        data = {}
        data_sources = ['fidelity', 'ystockquotelib']
        data_source_groups = ['example', 'example']
        customer_id = "FILL_ME_IN"
        password = "FILL_ME_IN"
        account_id = "FILL_ME_IN"
        email = "FILL_ME_IN"
        data_source_args = [['-c', customer_id, '-p', password, '-a', account_id, '-e', email], []]
        data = runner.run_batch(data, data_sources, data_source_groups, data_source_args)
        
        self.assertTrue(len(data.keys())) 


    # Just here in case you want to skip this one while running others manually
    # @unittest.skip('')
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


    # Just here in case you want to skip this one while running others manually
    # @unittest.skip('')
    def test_schema_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual_keys = runner.get_schema(data_source, data_source_group, args)
        
        expected_keys = set(['AAPL', 'MSFT'])
        
        self.assertTrue(expected_keys == set(actual_keys))


if __name__ == '__main__':  
    unittest.main()

