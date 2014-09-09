import unittest
import sofine.data_format_plugins.format_xml as format_xml


class FormatXmlTestCase(unittest.TestCase):

    def _remove_whitespace(self, xml_str):
        xml_str = xml_str.replace(' ', '')
        xml_str = xml_str.replace('\n', '')
        return xml_str


    def test_deserialize(self):
        data = self._remove_whitespace("""
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        expected = {"AAPL": []}
        actual = format_xml.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_two_keys(self):
        data = self._remove_whitespace("""
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                            <row>
                                <key>MSFT</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        expected = {"AAPL": [], "MSFT": []}
        actual = format_xml.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_row_with_value(self):
        data = self._remove_whitespace("""
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        expected = {"AAPL": [{"x": "1"}]}
        actual = format_xml.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_row_with_values(self):
        data = self._remove_whitespace("""
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>y</attribute_key>
                                        <attribute_value>2</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        expected = {"AAPL": [{"x": "1"}, {"y": "2"}]}
        actual = format_xml.deserialize(data)
        self.assertTrue(expected == actual)


    def test_deserialize_rows_with_values(self):
        data = self._remove_whitespace("""
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>y</attribute_key>
                                        <attribute_value>2</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                            <row>
                                <key>MSFT</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>a</attribute_key>
                                        <attribute_value>10</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>b</attribute_key>
                                        <attribute_value>20</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        expected = {"AAPL": [{"x": "1"}, {"y": "2"}], "MSFT" : [{"a": "10"}, {"b": "20"}]}
        actual = format_xml.deserialize(data)
        self.assertTrue(expected == actual)


    def test_serialize(self):
        data = {"AAPL": []}
        expected = self._remove_whitespace("""  
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        actual = self._remove_whitespace(format_xml.serialize(data))
        self.assertTrue(expected == actual)


    def test_serialize_two_keys(self):
        data = {"AAPL": [], "MSFT": []}
        expected = self._remove_whitespace("""  
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                            <row>
                                <key>MSFT</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key/>
                                        <attribute_value/>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        actual = self._remove_whitespace(format_xml.serialize(data))
        self.assertTrue(expected == actual)


    def test_serialize_row_with_value(self):
        data = {"AAPL": [{"x": "1"}]}
        expected = self._remove_whitespace("""  
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        actual = self._remove_whitespace(format_xml.serialize(data))
        self.assertTrue(expected == actual)


    def test_serialize_row_with_values(self):
        data = {"AAPL": [{"x": "1"}, {"y": "2"}]}
        expected = self._remove_whitespace("""  
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>y</attribute_key>
                                        <attribute_value>2</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        actual = self._remove_whitespace(format_xml.serialize(data))
        self.assertTrue(expected == actual)


    def test_serialize_rows_with_values(self):
        data = {"AAPL": [{"x": "1"}, {"y": "2"}], "MSFT" : [{"a": "10"}, {"b": "20"}]}
        expected = self._remove_whitespace("""  
                        <data>
                            <row>
                                <key>AAPL</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>x</attribute_key>
                                        <attribute_value>1</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>y</attribute_key>
                                        <attribute_value>2</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                            <row>
                                <key>MSFT</key>
                                <attributes>
                                    <attribute>
                                        <attribute_key>a</attribute_key>
                                        <attribute_value>10</attribute_value>
                                    </attribute>
                                    <attribute>
                                        <attribute_key>b</attribute_key>
                                        <attribute_value>20</attribute_value>
                                    </attribute>
                                </attributes>
                            </row>
                        </data>""")
        actual = self._remove_whitespace(format_xml.serialize(data))
        self.assertTrue(expected == actual)


if __name__ == '__main__':
    unittest.main()

