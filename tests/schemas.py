"""JSON schemas for API response validation."""

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id":    {"type": "integer"},
        "name":  {"type": "string"},
        "email": {"type": "string"},
    },
    "additionalProperties": False,
}

USER_LIST_SCHEMA = {
    "type": "array",
    "items": USER_SCHEMA,
    "minItems": 1,
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {"type": "string"},
    },
}
