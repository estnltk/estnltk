from html import escape
import pandas
import regex as re

from estnltk_core.common import OUTPUT_CONFIG

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
    html_str_max_len = OUTPUT_CONFIG.get('html_str_max_len', 100)
    if len(value_str) >= html_str_max_len:
        value_str = value_str[:max(html_str_max_len-20, 20)] + ' ..., type: ' + str(type(value))
        if hasattr(value, '__len__'):
            value_str += ', length: ' + str(len(value))

    if escape_html:
        value_str = escape(value_str)
    return value_str


def span_html_text(span, margin):
    base = span.base_span.flatten()
    if span.text_object is not None:
        raw_text = span.text_object.text

        start, last_end = base[0]
        html_parts = ['<span style="font-family: monospace; white-space: pre-wrap;">',
                      escape(raw_text[max(0, start-margin):start]),
                      '<span style="text-decoration: underline;">',
                      escape(raw_text[start:last_end]),
                      '</span>']

        for start, end in base[1:]:
            html_parts.append(escape(raw_text[last_end:start]))
            html_parts.append('<span style="text-decoration: underline;">')
            html_parts.append(escape(raw_text[start:end]))
            html_parts.append('</span>')
            last_end = end

        html_parts.append(escape(raw_text[last_end:last_end+margin]))

        html_parts.append('</span>')
    else:
        html_parts = ['<span style="font-family: monospace; white-space: pre-wrap;">']
        html_parts.append('<span>')
        html_parts.append( str(None) )
        html_parts.append('</span>')
        html_parts.append('</span>')
    return ''.join(html_parts)


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
                record['text'] = span_html_text(span, margin)
            else:
                record[''] = ''
                record['text'] = ''
            records.append(record)
            first = False
    df = pandas.DataFrame.from_records(records, columns=columns)
    return df.to_html(index=False, escape=False)
