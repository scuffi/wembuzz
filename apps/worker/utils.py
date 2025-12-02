import hashlib
import json


def generate_event_key(args: dict) -> str:
    return hashlib.sha256(json.dumps(args).encode()).hexdigest()
