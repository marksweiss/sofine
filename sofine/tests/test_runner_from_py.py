import unittest
import sys
import sofine.runner as runner
import sofine.lib.utils.utils as utils


class TestCase(unittest.TestCase):
    
    def test_runner_mock(self):
        data = {"AAPL" : [], "MSFT" : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock'
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


    def test_runner_mock_namespaced(self):
        data = {"AAPL" : [], "MSFT" : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock'
        data_source_args = []
        data = runner.get_namespaced_data(data, data_source, data_source_group, data_source_args)
        
        actual_keys = set(data.keys())
        expected_keys = set(['AAPL', 'MSFT'])

        self.assertTrue(expected_keys == actual_keys)
        for k in actual_keys:
            self.assertTrue(len(data[k]))
            for attr in data[k]:
                for k,v in attr.iteritems():
                    self.assertTrue(k is not None and k.startswith('mock::ystockquotelib_mock::') and v is not None)
   

    def test_runner_file_source(self):
        data = {}
        data_source = 'file_source'
        data_source_group = 'standard'
        # This path needs to match the path relative to file_source.py
        #  where the code using the path variable to find the test data file runs
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        data_source_args = ['-p', path]
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
       
        actual_keys = set(data.keys())
        expected_keys = set(['AAPL', 'MSFT']) 
        self.assertTrue(expected_keys == actual_keys)


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
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        data_source_args = ['-p', path]
        data = runner.get_data(data, data_source, data_source_group, data_source_args)
        
        expected_keys = set(['AAPL', 'MSFT'])
        
        self.assertTrue(expected_keys == set(data.keys()))


    def test_get_keys_file_source(self):
        data = {}
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        
        data = runner.get_data(data, data_source, data_source_group, args)
        keys_from_data = set(data.keys())
        
        plugin_mod = runner.get_plugin_module(data_source, data_source_group)
        keys_from_get_keys = set(plugin_mod.get_keys(path))
        
        self.assertTrue(keys_from_data == keys_from_get_keys)


    def test_adds_keys_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        actual = runner.adds_keys(data_source, data_source_group)
        expected = True
        self.assertTrue(actual['adds_keys'] == expected)


    def test_parse_args_file_source(self):
        data_source = 'file_source'
        data_source_group = 'standard'
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        args = ['-p', path]
        actual = runner.parse_args(data_source, data_source_group, args)

        self.assertTrue(actual['is_valid'] and actual['parsed_args'] == [path])

    
    def test_get_schema(self):
        data = {'AAPL' : []}
        data_source = 'ystockquotelib_mock'
        data_source_group = 'mock'
        args = []
        data = runner.get_data(data, data_source, data_source_group, args)
        schema = runner.get_schema(data_source, data_source_group)
        attr_keys = [attr.keys()[0] for attr in data['AAPL']]
        self.assertTrue(set(attr_keys) == set(schema['schema']))


    def test_runner_get_data_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'mock']
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        file_source_args = ['-p', path]
        ystockquote_args = []
        data_source_args = [file_source_args, ystockquote_args]
        
        data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))
        self.assertTrue(len(data['AAPL']) and len(data['MSFT'])) 


    def test_runner_get_namespaced_data_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'mock']
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        file_source_args = ['-p', path]
        ystockquote_args = []
        data_source_args = [file_source_args, ystockquote_args]
        
        data = runner.get_namespaced_data_batch(data, data_sources, data_source_groups, data_source_args)
        
        self.assertTrue(set(data.keys()) == set(['AAPL', 'MSFT']))
        self.assertTrue(len(data['AAPL']) and len(data['MSFT'])) 
       
        for k in data.keys():
            self.assertTrue(len(data[k]))
            for attr in data[k]:
                for k,v in attr.iteritems():
                    self.assertTrue(k is not None and 
                            (k.startswith('mock::ystockquotelib_mock::') or k.startswith('standard::file_source::'))
                            and v is not None)


    def test_runner_get_data_batch(self):
        data = {}
        data_sources = ['file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'mock']
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
        data_sources = ['file_source', 'file_source', 'ystockquotelib_mock']
        data_source_groups = ['standard', 'standard', 'mock']
        
        path_1 = './sofine/tests/fixtures/file_source_test_data.txt'
        file_source_args_1 = ['-p', path_1]
        path_2 = './sofine/tests/fixtures/file_source_test_data_2.txt'
        file_source_args_2 = ['-p', path_2]
        ystockquote_args = []
        
        data_source_args = [file_source_args_1, file_source_args_2, ystockquote_args]
        data = runner.get_data_batch(data, data_sources, data_source_groups, data_source_args)

        # Use the runner interface to get a plugin module to call the public 
        #  module-scope helper defined in file_source, get_keys(). This lets us
        #  pass in a path and get back the keys that that file_source config
        #  at that path adds.
        # This design pattern of being able to retrieve a module is useful in general
        #  for plugin implementations that want to expose module-scope attributes
        #  and helper. Here it lets us introspect state that the module can access.
        #  This could be useful in many situations besides testing. For example,
        #  the very thing we are doing here, looking at which step in a pipeline
        #  added which keys, might be useful in other situations.
        file_source_plug_mod = runner.get_plugin_module('file_source', 'standard')
        file_source_keys_1 = file_source_plug_mod.get_keys(path_1)
        file_source_keys_2 = file_source_plug_mod.get_keys(path_2)

        # Assert that final output has keys from each file_source step
        for k in file_source_keys_1:
            self.assertTrue(k in data)
        for k in file_source_keys_2:
            self.assertTrue(k in data)
        # Assert that the final output has values from ystockquotelib_mock for 
        #  keys added by file_source
        for k in file_source_keys_1:
            self.assertTrue(len(data[k]))
        for k in file_source_keys_2:
            self.assertTrue(len(data[k]))


if __name__ == '__main__':  
    unittest.main()

