import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner
import sofine.lib.utils.utils as utils

class TestCase(unittest.TestCase):
    
    def test_runner_get_data_google_search_results(self):
        key = 'AAPL'
        data = {key : []}
        data_source = 'google_search_results'
        data_source_group = 'example_http'
        data_source_args = []
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : [], key2 : []}
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        # Assert that we have data for each key
        self.assertTrue(data[key])
        self.assertTrue(data[key2])


if __name__ == '__main__':  
    unittest.main()

