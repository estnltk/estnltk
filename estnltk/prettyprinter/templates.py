def header():
    return """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>\n"""
def middle():
    return """
    </style>
    <body>
        <p>
"""
def footer():
    return """\t</body>\n</html>"""
def cssHeader():
    return """mark {
    color: black;
    background-color: white;
    font-family: "Times New Roman", Times, serif;
    font-weight: normal;
    font-style: normal;
    text-decoration: none;
    font-size: 30px;
    letter-spacing: 2px;
    }\n"""

def safe_get(dictList, key, default):
    if key in dictList:
        return dictList[key]
    else:
        return default
