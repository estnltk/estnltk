import json
from . import export_dict

def export_json(text:'Text', file:str=None, file_encoding:str='utf-8'):
    """Exports text object to json.
    If file is None, returns json string,
    otherwise dumps json string to file and returns None.
    
    Note: on the Windows platform, writing a text file 
    without specifying the encoding likely raises 
    "UnicodeEncodeError: 'charmap' codec can't encode 
    character ...", so the parameter file_encoding 
    (default: 'utf-8') must be used to reinforce the 
    encoding.
    """
    text_dict = export_dict(text)
    if file:
        with open(file, 'w', encoding=file_encoding) as out_f:
            json.dump(text_dict, fp=out_f, ensure_ascii=False)
    else:
        return json.dumps(text_dict, ensure_ascii=False)
