
import uuid

callback_mapping = {}
def set_callback_payload(data: dict) -> str:
    """Store the payload in the mapping and return a short key."""
    key = f"cb_{uuid.uuid4().hex[:8]}"
    callback_mapping[key] = data
    return key

def get_callback_payload(key: str) -> dict:
    """Retrieve the payload by key."""
    return callback_mapping.get(key, {})

def set_callback_data(prefix, value):
    key = f"{prefix}_{uuid.uuid4().hex[:8]}"
    callback_mapping[key] = value
    return key


def get_callback_data(key):
    return callback_mapping.get(key)
