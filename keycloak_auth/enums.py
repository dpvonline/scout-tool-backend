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


class PermissionType(str, Enum):
    ADMIN = 'admin'
    VIEW = 'view'


def jsonify(payload):
    payload_dict = asdict(payload)
    payload_filtered = {v: payload_dict[v] for v in payload_dict if payload_dict[v] is not None}
    payload_json = json.dumps(payload_filtered)
    return payload_json
