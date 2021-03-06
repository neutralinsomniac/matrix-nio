# -*- coding: utf-8 -*-

# Copyright © 2018 Damir Jelić <poljar@termina.org.uk>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import unicode_literals

from jsonschema import Draft4Validator, FormatChecker, validators

RoomRegex = "^![a-zA-Z0-9]+:.+$"
UserIdRegex = "^@.*:.+$"
EventTypeRegex = r"^.+\..+"
Base64Regex = r"[^-A-Za-z0-9+/=]|=[^=]|={3,}$"
KeyRegex = r"(ed25519|curve25519):.+"
SignedCurveRegex = r"(signed_curve25519|curve25519):.+"


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema
        ):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})


Validator = extend_with_default(Draft4Validator)


@FormatChecker.cls_checks("user_id", ValueError)
def check_user_id(value):
    # type: (str) -> bool
    if not value.startswith("@"):
        raise ValueError("UserIDs start with @")

    if ":" not in value:
        raise ValueError(
            "UserIDs must have a domain component, seperated by a :"
        )

    return True


def validate_json(instance, schema):
    Validator(schema, format_checker=FormatChecker()).validate(instance)


class Schemas(object):
    room_message = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {"msgtype": {"type": "string"}},
                "required": ["msgtype"],
            }
        },
    }

    room_message_text = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "msgtype": {"type": "string", "const": "m.text"},
                    "body": {"type": "string"},
                    "formatted_body": {"type": "string"},
                    "format": {"type": "string"},
                },
                "required": ["msgtype", "body"],
            }
        },
    }

    room_message_emote = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "msgtype": {"type": "string", "const": "m.emote"},
                    "body": {"type": "string"},
                    "formatted_body": {"type": "string"},
                    "format": {"type": "string"},
                },
                "required": ["msgtype", "body"],
            }
        },
    }

    room_message_notice = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "msgtype": {"type": "string", "const": "m.notice"},
                    "body": {"type": "string"},
                },
                "required": ["msgtype", "body"],
            }
        },
    }

    room_message_media = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "body": {"type": "string"},
                    "url": {"type": "string"},
                    "msgtype": {
                        "type": "string",
                        "enum": ["m.image", "m.audio", "m.video", "m.file"],
                    },
                },
                "required": ["body", "url", "msgtype"],
            }
        },
    }

    room_encrypted_media = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "body": {"type": "string"},
                    "msgtype": {
                        "type": "string",
                        "enum": ["m.image", "m.audio", "m.video", "m.file"],
                    },
                    "file": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "hashes": {
                                "type": "object",
                                "properties": {
                                    "sha256": {"type": "string"}
                                }
                            },
                            "iv": {"type": "string"},
                            "key": {
                                "type": "object",
                                "properties": {
                                    "alg": {"type": "string"},
                                    "k": {"type": "string"},
                                },
                                "required": ["alg", "k"],
                            },
                        },
                    },
                    "required": ["url", "hashes", "iv", "key"],
                },
                "required": ["body", "file", "msgtype"],
            }
        },
        "required": ["content"],
    }

    redacted_event = {
        "type": "object",
        "properties": {
            "unsigned": {
                "type": "object",
                "properties": {
                    "redacted_because": {
                        "type": "object",
                        "properties": {
                            "sender": {"type": "string", "format": "user_id"},
                            "content": {
                                "type": "object",
                                "properties": {"reason": {"type": "string"}},
                            },
                        },
                        "required": ["sender", "content"],
                    }
                },
                "required": ["redacted_because"],
            }
        },
        "required": ["unsigned"],
    }

    login = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "user_id"},
            "device_id": {"type": "string"},
            "access_token": {"type": "string"},
        },
        "required": ["user_id", "device_id", "access_token"],
    }

    error = {
        "type": "object",
        "properties": {
            "error": {"type": "string"},
            "errcode": {"type": "string"},
        },
        "required": ["error", "errcode"],
    }

    room_timeline = {
        "type": "object",
        "properties": {
            "events": {"type": "array"},
            "limited": {"type": "boolean"},
            "prev_batch": {"type": "string"},
        },
        "required": ["events", "limited", "prev_batch"],
    }

    sync = {
        "type": "object",
        "properties": {
            "device_one_time_keys_count": {
                "type": "object",
                "properties": {
                    "curve25519": {"type": "integer", "default": 0},
                    "signed_curve25519": {"type": "integer", "default": 0},
                }
            },
            "device_lists": {
                "type": "object",
                "properties": {
                    "changed": {"type": "array", "items": {"type": "string"}},
                    "left": {"type": "array", "items": {"type": "string"}}
                }
            },
            "next_batch": {"type": "string"},
            "rooms": {
                "type": "object",
                "properties": {
                    "invite": {
                        "type": "object",
                        "patternProperties": {
                            RoomRegex: {
                                "type": "object",
                                "properties": {
                                    "invite_state": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    }
                                },
                                "required": ["invite_state"]
                            }
                        },
                        "additionalProperties": False,
                    },
                    "join": {
                        "type": "object",
                        "patternProperties": {
                            RoomRegex: {
                                "type": "object",
                                "properties": {
                                    "timeline": room_timeline,
                                    "state": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    },
                                    "ephemeral": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    },
                                    "summary": {
                                        "type": "object",
                                        "properties": {
                                            "m.invited_member_count": {
                                                "type": "integer"
                                            },
                                            "m.joined_member_count": {
                                                "type": "integer"
                                            },
                                            "m.heroes": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                        }
                                    },
                                    "account_data": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    },
                                },
                                "required": [
                                    "timeline",
                                    "state",
                                    "ephemeral",
                                    "account_data",
                                ]
                            }
                        },
                        "additionalProperties": False,
                    },
                    "leave": {
                        "type": "object",
                        "patternProperties": {
                            RoomRegex: {
                                "type": "object",
                                "properties": {
                                    "timeline": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    },
                                    "state": {
                                        "type": "object",
                                        "properties": {
                                            "events": {"type": "array"}
                                        },
                                        "required": ["events"]
                                    }
                                },
                                "required": ["timeline", "state"]
                            }
                        },
                        "additionalProperties": False,
                    },
                },
            },
            "to_device": {
                "type": "object",
                "properties": {
                    "events": {"type": "array"}
                },
                "required": ["events"]
            },
        },
        "required": [
            "next_batch",
            "device_one_time_keys_count",
            "device_lists",
            "rooms",
            "to_device",
        ],
    }

    room_event = {
        "type": "object",
        "properties": {
            "event_id": {"type": "string"},
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "unsigned": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string"},
                }
            },
        },
        "required": ["event_id", "sender", "type"],
    }

    room_state = {
        "type": "object",
        "properties": {"events": {"type": "array"}},
        "required": ["events"],
    }

    to_device = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "content": {"type": "object"},
        },
        "required": ["sender", "type", "content"],
    }

    room_encrypted = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "sender_key": {"type": "string"},
                    "algorithm": {"type": "string"}
                },
                "required": ["sender_key", "algorithm"],
            }
        },
        "required": ["content"],
    }

    room_olm_encrypted = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["m.room.encrypted"]},
            "content": {
                "type": "object",
                "properties": {
                    "sender_key": {"type": "string"},
                    "algorithm": {
                        "type": "string",
                        "enum": ["m.olm.v1.curve25519-aes-sha2"]
                    },
                    "ciphertext": {
                        "type": "object",
                        "patternProperties": {
                            Base64Regex: {
                                "type": "object",
                                "properties": {
                                    "body": {"type": "string"},
                                    "type": {"type": "integer"},
                                },
                                "required": ["type", "body"]
                            }
                        },
                    }
                },
                "required": ["sender_key", "algorithm", "ciphertext"]
            },
        },
        "required": [
            "type",
            "content",
        ],
    }

    room_megolm_decrypted = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {"type": "object"}
        },
        "required": [
            "type",
            "content",
        ],
    }

    room_megolm_encrypted = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["m.room.encrypted"]},
            "room_id": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "sender_key": {"type": "string"},
                    "algorithm": {
                        "type": "string",
                        "enum": ["m.megolm.v1.aes-sha2"]
                    },
                    "ciphertext": {"type": "string"},
                    "session_id": {"type": "string"},
                    "device_id": {"type": "string"},
                },
                "required": [
                    "sender_key",
                    "algorithm",
                    "ciphertext",
                    "session_id",
                    "device_id",
                ]
            },
        },
        "required": [
            "type",
            "content",
        ],
    }

    olm_event = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "sender_device": {"type": "string"},
            "keys": {
                "type": "object",
                "properties": {"ed25519": {"type": "string"}},
            },
            "recipient": {"type": "string", "format": "user_id"},
            "recipient_keys": {
                "type": "object",
                "properties": {"ed25519": {"type": "string"}},
            },
            "type": {"type": "string"},
            "content": {"type": "object"},
        },
        "required": [
            "type",
            "sender",
            "sender_device",
            "keys",
            "recipient",
            "recipient_keys",
            "content",
        ],
    }

    room_key_event = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "sender_device": {"type": "string"},
            "type": {"type": "string", "enum": ["m.room_key"]},
            "content": {
                "type": "object",
                "properties": {
                    "algorithm": {"type": "string"},
                    "room_id": {"type": "string", "format": "room_id"},
                    "session_id": {"type": "string"},
                    "session_key": {"type": "string"},
                    "chain_index": {"type": "integer"},
                },
                "required": [
                    "algorithm",
                    "room_id",
                    "session_id",
                    "session_key",
                ],
            },
        },
        "required": ["type", "sender", "sender_device", "content"],
    }

    room_canonical_alias = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {"alias": {"type": "string"}},
                "required": ["alias"],
            },
        },
        "required": ["type", "sender", "content"],
    }

    room_name = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        "required": ["type", "sender", "content"],
    }

    room_topic = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {"topic": {"type": "string"}},
                "required": ["topic"],
            },
        },
        "required": ["type", "sender", "content"],
    }

    room_power_levels = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "ban": {"type": "integer", "default": 50},
                    "kick": {"type": "integer", "default": 50},
                    "invite": {"type": "integer", "default": 50},
                    "redact": {"type": "integer", "default": 50},
                    "users_default": {"type": "integer", "default": 0},
                    "events_default": {"type": "integer", "default": 0},
                    "state_default": {"type": "integer", "default": 50},
                    "events": {
                        "type": "object",
                        "default": {},
                        "patternProperties": {
                            EventTypeRegex: {"type": "integer"}
                        },
                        "additionalProperties": False,
                    },
                    "users": {
                        "type": "object",
                        "default": {},
                        "patternProperties": {
                            UserIdRegex: {"type": "integer"}
                        },
                        "additionalProperties": False,
                    },
                },
            },
        },
        "required": ["type", "sender", "content"],
    }

    room_membership = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "state_key": {"type": "string", "format": "user_id"},
            "type": {"type": "string", "enum": ["m.room.member"]},
            "prev_content": {
                "type": "object",
                "properties": {
                    "membership": {
                        "type": "string",
                        "enum": ["invite", "join", "knock", "leave", "ban"],
                    },
                    "avatar_url": {"type": ["string", "null"]},
                    "displayname": {"type": ["string", "null"]},
                },
                "required": ["membership"],
            },
            "content": {
                "type": "object",
                "properties": {
                    "membership": {
                        "type": "string",
                        "enum": ["invite", "join", "knock", "leave", "ban"],
                    },
                    "reason": {"type": ["string", "null"]},
                    "avatar_url": {"type": ["string", "null"]},
                    "displayname": {"type": ["string", "null"]},
                },
                "required": ["membership"],
            },
        },
        "required": ["type", "sender", "state_key", "content"],
    }

    room_redaction = {
        "type": "object",
        "properties": {
            "sender": {"type": "string", "format": "user_id"},
            "redacts": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
            },
        },
        "required": ["sender", "redacts"],
    }

    room_event_id = {
        "type": "object",
        "properties": {"event_id": {"type": "string"}},
        "required": ["event_id"],
        "additionalProperties": False,
    }

    room_id = {
        "type": "object",
        "properties": {"room_id": {"type": "string"}},
        "required": ["room_id"],
        "additionalProperties": False,
    }

    room_messages = {
        "type": "object",
        "properties": {
            "chunk": {"type": "array"},
            "start": {"type": "string"},
            "end": {"type": "string"},
        },
        "required": ["chunk", "start", "end"],
        "additionalProperties": False,
    }

    ephemeral_event = {
        "type": "object",
        "properties": {
            "content": {"type": "object"},
            "type": {"type": "string"}
        },
        "required": ["content", "type"],
    }

    m_typing = {
        "type": "object",
        "properties": {
            "content": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["user_ids"]
            },
            "type": {"type": "string"}
        },
        "required": ["content", "type"],
        "additionalProperties": False,
    }

    keys_upload = {
        "type": "object",
        "properties": {
            "one_time_key_counts": {
                "type": "object",
                "properties": {
                    "curve25519": {"type": "integer", "default": 0},
                    "signed_curve25519": {"type": "integer", "default": 0},
                },
            },
        },
        "required": ["one_time_key_counts"],
    }

    keys_query = {
        "type": "object",
        "properties": {
            "device_keys": {
                "type": "object",
                "patternProperties": {UserIdRegex: {
                    "type": "object",
                    "patternProperties": {r".+": {
                        "type": "object",
                        "properties": {
                            "algorithms": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "device_id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "keys": {
                                "type": "object",
                                "patternProperties": {
                                    KeyRegex: {"type": "string"}
                                },
                            },
                            "signatures": {
                                "type": "object",
                                "patternProperties": {
                                    UserIdRegex: {
                                        "type": "object",
                                        "patternProperties": {
                                            KeyRegex: {"type": "string"}
                                        }
                                    }
                                },
                            },
                        },
                        "required": [
                            "algorithms",
                            "device_id",
                            "keys",
                            "signatures"
                        ]
                    }}
                }},
            },
            "failures": {
                "type": "object"
            }
        },
        "required": ["device_keys", "failures"],
    }

    keys_claim = {
        "type": "object",
        "properties": {
            "one_time_keys": {
                "type": "object",
                "patternProperties": {UserIdRegex: {
                    "type": "object",
                    "patternProperties": {r".+": {
                        "type": "object",
                        "properties": {
                            "patternProperties": {SignedCurveRegex: {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "str"},
                                    "signatures": {
                                        "type": "object",
                                        "patternProperties": {UserIdRegex: {
                                            "type": "object",
                                            "patternProperties": {KeyRegex: {
                                                "type": "string"
                                            }}
                                        }},
                                    },
                                },
                                "required": [
                                    "key",
                                    "signatures"
                                ]
                            }},
                        }
                    }}
                }}
            },
            "failures": {
                "type": "object"
            }
        },
        "required": ["one_time_keys", "failures"],
    }

    devices = {
        "type": "object",
        "properties": {
            "devices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "display_name": {"type": ["string", "null"]},
                        "last_seen_ip": {"type": ["string", "null"]},
                        "last_seen_ts": {"type": ["integer", "null"]},
                    },
                    "required": [
                        "device_id",
                        "display_name",
                        "last_seen_ip",
                        "last_seen_ts"
                    ]
                }
            },
            "required": ["devices"]
        },
    }

    delete_devices = {
        "type": "object",
        "properties": {
            "session": {"type": "string"},
            "flows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "stages": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "required": ["stages"]
                    },
                }
            },
            "params": {
                "type": "object",
                "patternProperties": {r".+": {
                    "type": "object",
                    "patternProperties": {r".+": {"type": "string"}}
                }},
            },
            "required": ["session", "flows", "params"]
        },
    }

    joined_members = {
        "type": "object",
        "properties": {
            "joined": {
                "type": "object",
                "patternProperties": {UserIdRegex: {
                    "type": "object",
                    "properties": {
                        "avatar_url": {"type": ["string", "null"]},
                        "display_name": {"type": ["string", "null"]},
                    },
                    "required": ["display_name"]
                }}
            }
        },
        "required": ["joined"]
    }

    call_invite = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string"},
                    "lifetime": {"type": "integer"},
                    "version": {"type": "integer"},
                    "offer": {"type": "object"},
                },
                "required": [
                    "call_id",
                    "lifetime",
                    "version",
                    "offer",
                ]
            }
        },
        "required": [
            "type",
            "content",
        ],
    }

    call_answer = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string"},
                    "version": {"type": "integer"},
                    "answer": {"type": "object"},
                },
                "required": [
                    "call_id",
                    "version",
                    "answer",
                ]
            }
        },
        "required": [
            "type",
            "content",
        ],
    }

    call_hangup = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string"},
                    "version": {"type": "integer"},
                },
                "required": [
                    "call_id",
                    "version",
                ]
            }
        },
        "required": [
            "type",
            "content",
        ],
    }

    call_candidates = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string"},
                    "version": {"type": "integer"},
                    "candidates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "candidate": {"type": "string"},
                                "sdpMLineIndex": {"type": "integer"},
                                "sdpMid": {"type": "string"},
                            },
                            "required": [
                                "candidate",
                                "sdpMLineIndex",
                                "sdpMid"
                            ]
                        }
                    }
                },
                "required": [
                    "call_id",
                    "version",
                    "candidates"
                ]
            }
        },
        "required": [
            "type",
            "content",
        ],
    }

    account_data = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {"type": "object"}
        },
        "required": [
            "type",
            "content",
        ],
    }

    fully_read = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "content": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                },
                "required": [
                    "event_id",
                ]
            }
        },
        "required": [
            "type",
            "content",
        ],
    }

    upload = {
        "type": "object",
        "properties": {"content_uri": {"type": "string"}},
        "required": ["content_uri"],
        "additionalProperties": False,
    }

    empty = {"type": "object", "properties": {}, "additionalProperties": False}
