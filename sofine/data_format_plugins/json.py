import json


def deserialize(data):
    return json.loads(data)


def serialize(data):
    return json.dumps(data)

