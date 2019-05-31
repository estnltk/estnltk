from html import escape
import pandas
import regex as re


def to_str(value, escape_html=False):
    if isinstance(value, str):
        value_str = value
    elif callable(value) and hasattr(value, '__name__') and hasattr(value, '__module__'):
        value_str = '<function {}.{}>'.format(value.__module__, value.__name__)
    elif isinstance(value, re.regex.Pattern):
        value_str = '<Regex {}>'.format(value.pattern)
    elif isinstance(value, tuple):
        value_str = str(tuple(to_str(v) for v in value))
    else:
        value_str = str(value)

    if len(value_str) >= 100:
        value_str = value_str[:80] + ' ..., type: ' + str(type(value))
        if hasattr(value, '__len__'):
            value_str += ', length: ' + str(len(value))

    if escape_html:
        value_str = escape(value_str)
    return value_str


def html_text(raw_text, start, end, margin: int = 0):
    left = escape(raw_text[max(0, start - margin):start])
    middle = escape(raw_text[start:end])
    right = escape(raw_text[end:end + margin])
    return ''.join(('<span style="font-family: monospace; white-space: pre-wrap;">',
                    left,
                    '<span style="text-decoration: underline;">', middle, '</span>',
                    right, '</span>'))


def html_table(spans, attributes, margin=0, index=False):
    if index is True:
        columns = ['', 'text', *attributes]
    else:
        columns = ['text', *attributes]
    records = []
    for i, span in enumerate(spans):
        first = True
        for annotation in span.annotations:
            record = {k: escape(to_str(annotation[k])) for k in attributes}
            if first:
                record[''] = i
                record['text'] = html_text(span.raw_text, span.start, span.end, margin)
            else:
                record[''] = ''
                record['text'] = ''
            records.append(record)
            first = False
    pandas.set_option('display.max_colwidth', -1)
    df = pandas.DataFrame.from_records(records, columns=columns)
    return df.to_html(index=False, escape=False)
