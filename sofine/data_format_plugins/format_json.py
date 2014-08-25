import json


def deserialize(data):
    """
Required for a data format plugin. Converts JSON into the Python objects used by `sofine`.
"""
    return json.loads(data)


def serialize(data):
    """
Required for a data format plugin. Converts Python objects used by `sofine` into JSON.
"""
    return json.dumps(data)


def get_content_type():
    """
Required for a data format plugin. Returns the value for the HTTP Content-Type header. 
"""
    return 'application/json'

