import json
from types import SimpleNamespace


def to_simple_namespace(content):
    return json.loads(json.dumps(content), object_hook=lambda d: SimpleNamespace(**d))


def to_json(content):
    return json.loads(json.dumps(content, default=lambda x: x.__dict__, sort_keys=False, indent=4))
