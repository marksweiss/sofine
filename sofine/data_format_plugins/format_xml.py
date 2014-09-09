from xml.etree import ElementTree as ElementTree
from collections import defaultdict


def deserialize(data):
    """
Required for a data format plugin. Converts XML into the Python objects used by `sofine`.

Expects XML conforming to the following schema:
    
    <data>
        <row>
            <key>KEY_1</key>
            <attributes>
                <attribute>
                    <attribute_key>ATTR_KEY_1</attribute_key>
                    <attribute_value>ATTR_VALUE_1</attribute_value>
                </attribute>
                ...
                ...
            </attributes>
        </row>
        ...
        ...
    </data>

Converts the XML to a Python dict in `sofine` format:

    {
        "KEY_1": [{"ATTR_KEY_1": "ATTR_VALUE_1"}, ...],
        ...
        ...
    }
"""
    ret = {}
    xml_data = ElementTree.fromstring(data)
    rows = xml_data.findall('row')
    for row in rows:
        key = row.find('key').text
        ret[key] = []
        attrs = row.find('attributes')
        attr_list = attrs.findall('attribute')
        for attr in attr_list:
            attr_key = attr.find('attribute_key').text
            attr_value = attr.find('attribute_value').text
            # NOTE: Schema supports null attribute values, but not attribute keys
            # TODO Document this
            if attr_key:
                ret[key].append({attr_key : attr_value})
    
    return ret


def serialize(data):
    """
Required for a data format plugin. Converts Python objects used by `sofine` into XML.

Converts a Python dict in `sofine` format:

    {
        "KEY_1": [{"ATTR_KEY_1": "ATTR_VALUE_1"}, ...],
        ...
        ...
    }

Returns XML conforming to the following schema:
    
    <data>
        <row>
            <key>KEY_1</key>
            <attributes>
                <attribute>
                    <attribute_key>ATTR_KEY_1</attribute_key>
                    <attribute_value>ATTR_VALUE_1</attribute_value>
                </attribute>
                ...
                ...
            </attributes>
        </row>
        ...
        ...
    </data>
"""
    root = ElementTree.Element('data') 
  

    def append_attr_node(attrs_node, attr_key, attr_value):
        attr_node = ElementTree.Element('attribute')
        attr_key_node = ElementTree.Element('attribute_key')
        attr_value_node = ElementTree.Element('attribute_value')
        attr_key_node.text = attr_key
        attr_value_node.text = attr_value
        attr_node.append(attr_key_node)
        attr_node.append(attr_value_node)
        attrs_node.append(attr_node)


    for key, attrs in data.iteritems():
        row_node = ElementTree.Element('row')
        root.append(row_node)
        key_node = ElementTree.Element('key')
        key_node.text = key
        row_node.append(key_node)
        attrs_node = ElementTree.Element('attributes')
        row_node.append(attrs_node)
        if len(attrs) == 0:
            attr_key = ''
            attr_value = ''
            append_attr_node(attrs_node, attr_key, attr_value)
        else:
            for attr in attrs:
                attr_key = attr.keys()[0]
                attr_value = attr.values()[0]
                append_attr_node(attrs_node, attr_key, attr_value)

    return ElementTree.tostring(root, encoding='utf-8')


def get_content_type():
    """
Required for a data format plugin. Returns the value for the HTTP Content-Type header. 
"""
    return 'application/xml'

