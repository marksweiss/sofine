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
        data_source_args = []
        data = runner.run(data, data_source, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : {}, key2 : {}}
        data = runner.run(data, data_source, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])


    def test_schema_ystockquote(self):
        key = 'AAPL'
        data = {key : {}}
        data_source = 'ystockquotelib'
        data_source_args = []
        data = runner.run(data, data_source, data_source_args)
        
        expected_attributes = runner.get_schema(data_source)
        # Set intersection of actual keys and expected keys must have at least
        #  one element. ystockquotelib doesn't guarantee returning all keys
        #  found in schema as attribute keys for every key passed to it,
        #  but it does guarantee those keys will be a subset of the keys in schema.
        self.assertTrue(set(data[key].keys()) & set(expected_attributes))

    
    @unittest.skip("MUST RUN MANUALLY. ARGS INCLUDE SENSITIVE INFORMATION.")
    def test_runner_run_fidelity(self):
        customer_id = "FILL_ME_IN"
        password = "FILL_ME_IN"
        account_id = "FILL_ME_IN"
        email = "FILL_ME_IN"
        data = {}
        data_sources = 'fidelity'
        data_source_args = ["-c", customer_id, "-p", password, "-a", account_id, "-e", email]
        validate_args = True
        data = runner.run(data, data_sources, data_source_args)
        
        self.assertTrue(len(data.keys())) 

    
    @unittest.skip("MUST RUN MANUALLY. ARGS INCLUDE SENSITIVE INFORMATION.")
    def test_runner_run_batch(self):
        customer_id = "FILL_ME_IN"
        password = "FILL_ME_IN"
        account_id = "FILL_ME_IN"
        email = "FILL_ME_IN"
        data = {}
        data_sources = ['fidelity', 'ystockquotelib']
        data_source_args = [["-c", customer_id, "-p", password, "-a", account_id, "-e", email], []]
        validate_args = True
        data = runner.run(data, data_sources, data_source_args)
        
        self.assertTrue(len(data.keys())) 


if __name__ == '__main__':  
    unittest.main()

