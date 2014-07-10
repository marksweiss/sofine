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


    # Test composing operations where some are an initial source of keys, some
    #  add new keys in an intermediate step, and some just add attributes to keys
    # This thus starts with Fidelity, which is a source of keys based on the account
    #  args passed to it, then calls a file_source, which is a source that adds new
    #  keys to the existing set, and then calls Yahoo API, which will get attributes
    #  for all the keys you pass it
    #
    # So, this test is a good example of usage of the lib to build a simple pipeline,
    #  showing how each step can append new data to existing keys (and add new keys
    #  with attributes), or just add new keys with empty attributes, or add new keys
    #  with attributes.
    # 
    # ==> The end result of the pipeline is the union of each step.
    # @unittest.skip("MUST RUN MANUALLY. ARGS INCLUDE SENSITIVE INFORMATION.")
    def test_runner_pipeline(self):
        data = {}
        data_sources = ['fidelity', 'file_source', 'ystockquotelib']
        data_source_groups = ['example', 'standard', 'example']
        
        customer_id = "marksweiss"
        password = "abb123321"
        account_id = "169746010"
        email = "marksweiss@yahoo.com"
        fidelity_args = ['-c', customer_id, '-p', password, '-a', account_id, '-e', email]
        path = './tests/fixtures/file_source_test_data.txt'
        file_source_args = ['-p', path]
        ystockquote_args = []
        
        data_source_args = [fidelity_args, file_source_args, ystockquote_args]
        data = runner.run_batch(data, data_sources, data_source_groups, data_source_args)

        # Assert that final output has keys from the intermediate file_source step
        file_source_keys = runner.get_schema('file_source', 'standard', file_source_args)
        for k in file_source_keys:
            self.assertTrue(k in data)
        # Assert that the final output has values from ystockquotelib for 
        #  keys added by file_source
        for k in file_source_keys:
            self.assertTrue(len(data[k].keys()) > 0)


if __name__ == '__main__':  
    unittest.main()

