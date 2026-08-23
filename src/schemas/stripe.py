CUSTOMER_SCHEMA = {
    "type": "object",
    "required": ["id", "object", "livemode"],
    "properties": {
        "id": {"type": "string", "pattern": r"^cus_"},
        "object": {"const": "customer"},
        "livemode": {"type": "boolean"},
        "email": {"type": ["string", "null"]},
        "name": {"type": ["string", "null"]},
        "deleted": {"type": "boolean"},
    },
    "additionalProperties": True,
}

PAYMENT_INTENT_SCHEMA = {
    "type": "object",
    "required": ["id", "object", "amount", "currency", "status", "livemode"],
    "properties": {
        "id": {"type": "string", "pattern": r"^pi_"},
        "object": {"const": "payment_intent"},
        "amount": {"type": "integer", "minimum": 1},
        "currency": {"type": "string", "minLength": 3},
        "status": {"type": "string", "minLength": 1},
        "livemode": {"const": False},
    },
    "additionalProperties": True,
}

BALANCE_SCHEMA = {
    "type": "object",
    "required": ["object", "available", "pending", "livemode"],
    "properties": {
        "object": {"const": "balance"},
        "livemode": {"type": "boolean"},
        "available": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["amount", "currency"],
                "properties": {
                    "amount": {"type": "integer"},
                    "currency": {"type": "string"},
                },
            },
        },
        "pending": {"type": "array"},
    },
    "additionalProperties": True,
}

LIST_SCHEMA = {
    "type": "object",
    "required": ["object", "data", "has_more"],
    "properties": {
        "object": {"const": "list"},
        "data": {"type": "array"},
        "has_more": {"type": "boolean"},
    },
    "additionalProperties": True,
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["message", "type"],
            "properties": {
                "message": {"type": "string", "minLength": 1},
                "type": {"type": "string"},
                "code": {"type": ["string", "null"]},
                "param": {"type": ["string", "null"]},
            },
            "additionalProperties": True,
        }
    },
    "additionalProperties": True,
}

DELETED_CUSTOMER_SCHEMA = {
    "type": "object",
    "required": ["id", "object", "deleted"],
    "properties": {
        "id": {"type": "string"},
        "object": {"const": "customer"},
        "deleted": {"const": True},
    },
    "additionalProperties": True,
}
