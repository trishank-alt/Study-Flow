# Validation utilities for parsed JSON responses
def validate_dict_keys(data: dict, required_keys: list) -> bool:
    return all(k in data for k in required_keys)
