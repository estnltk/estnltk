# This is the mapping file for creating new indexes.
# It is somewhat more verbose than it needs to be, but it is explicit in its choices.
mapping = {
    "mappings": {
        "document": {
            "_all": {
                "enabled": False  # We rarely want to search over all fields
            },
            "properties": {
                "meta": {
                    "type": "object"
                }
            }
        },
        "flag": {
            "_all": {
                "enabled": False
            },
            "_parent": {
                "type": "sentence"
            },
            "properties": {
                "value": {
                    "doc_values": True,
                    "index": "not_analyzed",
                    "norms": {
                        "enabled": False
                    },
                    "type": "string"
                }
            }
        },
        "sentence": {
            "_all": {
                "enabled": False
            },
            "_parent": {
                "type": "document"
            },
            "properties": {
                "estnltk_text_object": {  # raw estnltk text object
                    "index": "no",  # not searchable
                    "store": True,  # but stored separately
                    "type": "string"  # Not analyzed, stored as text
                },
                "lemmas": {
                    "analyzer": "estnltk_lowercase",
                    "norms": {
                        "enabled": False
                    },
                    "type": "string",
                    "position_increment_gap": 100  # different analyses are separated by 100 positions
                },
                "meta": {
                    "properties": {
                        "order_in_parent": {
                            "doc_values": True,  # keep less information in memory
                            "norms": {  # do not compute data for scoring results
                                "enabled": False
                            },
                            "type": "long"
                        }
                    }
                },
                "postags": {
                    "analyzer": "estnltk_uppercase",
                    "norms": {
                        "enabled": False
                    },
                    "type": "string",
                    "position_increment_gap": 100
                },
                "text": {
                    "analyzer": "whitespace",
                    "norms": {
                        "enabled": False
                    },
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "words": {
                    "properties": {
                        "analysis": {
                            "properties": {
                                "clitic": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "ending": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "form": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "lemma": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "partofspeech": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "root": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                },
                                "root_tokens": {
                                    "doc_values": True,
                                    "index": "not_analyzed",
                                    "norms": {
                                        "enabled": False
                                    },
                                    "type": "string"
                                }
                            },
                            "type": "nested"
                        },
                        "text": {
                            "doc_values": True,
                            "index": "not_analyzed",
                            "norms": {
                                "enabled": False
                            },
                            "type": "string"
                        }
                    }
                }
            }
        }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "estnltk_lowercase": {
                    "filter": [
                        "lowercase"
                    ],
                    "tokenizer": "whitespace",
                    "type": "custom"
                },
                "estnltk_uppercase": {
                    "filter": [
                        "uppercase"
                    ],
                    "tokenizer": "whitespace",
                    "type": "custom"
                }
            }
        }
    }
}
