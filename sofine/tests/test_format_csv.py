import unittest
import sofine.data_format_plugins.format_csv as format_csv


class FormatCsvTestCase(unittest.TestCase):

    def test_deserialize(self):
        data = 'AAPL'
        expected = {"AAPL": []}
        actual = format_csv.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_two_keys(self):
        data = 'AAPL|MSFT'
        expected = {"AAPL": [], "MSFT": []}
        actual = format_csv.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_row_with_value(self):
        data = 'AAPL,x,1'
        expected = {"AAPL": [{"x": "1"}]}
        actual = format_csv.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_row_with_values(self):
        data = 'AAPL,x,1,y,2'
        expected = {"AAPL": [{"x": "1"}, {"y": "2"}]}
        actual = format_csv.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_rows_with_values(self):
        data = 'AAPL,x,1,y,2|MSFT,a,10,b,20'
        expected = {"AAPL": [{"x": "1"}, {"y": "2"}], "MSFT" : [{"a": "10"}, {"b": "20"}]}
        actual = format_csv.deserialize(data)
        self.assertTrue(expected == actual)


    def test_serialize(self):
        data = {"AAPL": []}
        expected = 'AAPL|'
        actual = format_csv.serialize(data)
        self.assertTrue(expected == actual)


    def test_serialize_two_keys(self):
        data = {"AAPL": [], "MSFT": []}
        expected = 'AAPL|MSFT|'
        actual = format_csv.serialize(data)
        self.assertTrue(expected == actual)


    def test_serialize_row_with_value(self):
        data = {"AAPL": [{"x": "1"}]}
        expected = 'AAPL,x,1|'
        actual = format_csv.serialize(data)
        self.assertTrue(expected == actual)


    def test_serialize_row_with_values(self):
        data = {"AAPL": [{"x": "1"}, {"y": "2"}]}
        expected = 'AAPL,x,1,y,2|'
        actual = format_csv.serialize(data)
        self.assertTrue(expected == actual)


    def test_serialize_rows_with_values(self):
        data = {"AAPL": [{"x": "1"}, {"y": "2"}], "MSFT" : [{"a": "10"}, {"b": "20"}]}
        expected = 'AAPL,x,1,y,2|MSFT,a,10,b,20|'
        actual = format_csv.serialize(data)
        self.assertTrue(expected == actual)


if __name__ == '__main__':
    unittest.main()

