import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner

class TestCase(unittest.TestCase):
    
    def test_runner_file_source(self):
        data = {}
        data_source = 'file_source'
        data_source_group = 'standard'
        # This path needs to match the path relative to file_source.py
        #  where the code using the path variable to find the test data file runs
        path = './tests/fixtures/file_source_test_data.txt'
        data_source_args = ['-p', path]
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))


    # To run:
    # - create a custom plugin directory for your plugins, outside the sofine project tree
    # - create a subdirectory in the custom plugin directory called 'test'
    # - make a copy of PROJECT_ROOT/sofine/plugins/standard/file_source.py as
    #   CUSTOM_PLUGIN_DIR/standard/file_source_custom_path.py
    # Uncomment the unittest.skip(True) attribute after above steps are completed
    @unittest.skip(True)
    def test_runner_file_source_custom_plugin_path(self):
        data = {}
        data_source = 'file_source_custom_path'
        data_source_group = 'standard'
        # This path needs to match the path relative to file_source.py
        #  where the code using the path variable to find the test data file runs
        path = './tests/fixtures/file_source_test_data.txt'
        data_source_args = ['-p', path]
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))


    def test_schema_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual_keys = runner.get_schema(data_source, data_source_group, args)
        
        expected_keys = set(['AAPL', 'MSFT'])
        
        self.assertTrue(expected_keys == set(actual_keys['schema']))


    def test_adds_keys_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        actual = runner.adds_keys(data_source, data_source_group)
        expected = True
        self.assertTrue(actual['adds_keys'] == expected)


    def test_parse_args_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual = runner.parse_args(data_source, data_source_group, args)

        self.assertTrue(actual['is_valid'] and actual['parsed_args'] == [path])


    def test_runner_get_data_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'mock']
        path = './tests/fixtures/file_source_test_data.txt'
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
        data_sources = ['file_source', 'file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'standard', 'mock']
        
        path = './tests/fixtures/file_source_test_data.txt'
        file_source_args_1 = ['-p', path]
        path_2 = './tests/fixtures/file_source_test_data_2.txt'
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
        # Assert that the final output has values from ystockquotelib_mock for 
        #  keys added by file_source
        for k in file_source_keys_1['schema']:
            self.assertTrue(len(data[k].keys()))
        for k in file_source_keys_2['schema']:
            self.assertTrue(len(data[k].keys()))


if __name__ == '__main__':  
    unittest.main()

