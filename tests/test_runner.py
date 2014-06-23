#!/anaconda/bin/python -tt

import unittest
import sys
sys.path.insert(0, '..')
import sofine.runner as runner

class TestCase(unittest.TestCase):
    
    def test_runner_ystockquote(self):
        key = 'AAPL'
        data = {key : {}}
        data_sources = ['ystockquotelib']
        data_source_args = [[]]
        validate_args = True
        data = runner.run(data, data_sources, data_source_args, validate_args)
        self.assertTrue(data[key])
        
        key2 = 'MSFT'
        data = {key : {}, key2 : {}}
        data = runner.run(data, data_sources, data_source_args, validate_args)
        self.assertTrue(data[key])
        self.assertTrue(data[key2])


if __name__ == '__main__':  
    unittest.main()
