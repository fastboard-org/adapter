from bson import ObjectId
import re


def replace_objectid_strings(data):
    if isinstance(data, dict):
        return {
            replace_objectid_strings(key): replace_objectid_strings(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [replace_objectid_strings(item) for item in data]
    elif isinstance(data, str):
        match = re.match(r"ObjectId\('([0-9a-fA-F]{24})'\)", data)
        if match:
            return ObjectId(match.group(1))
    return data
