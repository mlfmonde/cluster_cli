import json
from collections import namedtuple


def _json_object_hook(data):
    keys = [k.replace('-', '_') for k in data.keys()]
    return namedtuple('X', keys)(*data.values())


def json2obj(data):
    if not data:
        return None
    return json.loads(data, object_hook=_json_object_hook)
