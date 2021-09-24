import json


def to_json_file(obj, file: str, file_encoding: str = 'utf-8'):
    with open(file, 'w', encoding=file_encoding) as out_f:
        json.dump(obj, fp=out_f, ensure_ascii=False)


def from_json_file(file: str, file_encoding: str = 'utf-8'):
    with open(file, 'r', encoding=file_encoding) as in_f:
        return json.load(fp=in_f)


def to_json(obj):
    return json.dumps(obj, ensure_ascii=False)


def from_json(s):
    return json.loads(s)


