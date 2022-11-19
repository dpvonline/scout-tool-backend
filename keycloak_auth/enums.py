import json
from dataclasses import asdict
from enum import Enum


class DecisionStrategy(str, Enum):
    AFFIRMATIVE = "AFFIRMATIVE",
    UNANIMOUS = "UNANIMOUS",
    CONSENSUS = "CONSENSUS"


class Logic(str, Enum):
    POSITIVE = "POSITIVE",
    NEGATIVE = "NEGATIVE"


class PolicyType(str, Enum):
    ROLE = "role"
    RESOURCE = "resource"
    AGGREGATE = 'aggregate'


class PermissionType(str, Enum):
    ADMIN = 'admin'
    VIEW = 'view'
    MANAGE = 'manage'
    NONE = 'none'


def jsonify(payload, dumps=True):
    payload_dict = asdict(payload)
    payload_filtered = {v: payload_dict[v] for v in payload_dict if payload_dict[v] is not None}
    if dumps:
        payload_json = json.dumps(payload_filtered)
    else:
        payload_json = payload_filtered
    return payload_json
