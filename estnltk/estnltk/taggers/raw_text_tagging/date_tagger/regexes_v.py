import pandas as pd

MACROS = {
    'hour': r'[0-2][0-9]',
    'minute': r'[0-5][0-9]',
    'second': r'[0-5][0-9]',
    'DAY': r'(0?[1-9]|[12][0-9]|3[01])',
    'MONTH': r'(0?[1-9]|1[0-2])',
    'YEAR': r'((19[0-9]{2})|(20[0-9]{2})|([0-9]{2}))',
    'LONGYEAR': r'((19[0-9]{2})|(20[0-9]{2}))'
    
 }
 
for k, v in MACROS.items():
	MACROS[k] = r'(?P<{key}>{regex})'.format(key=k, regex=v)
 

MACROS['DATE'] = r'{DAY}\.\s*{MONTH}\.\s*{YEAR}'.format(**MACROS)
MACROS['TIME'] = r'{hour}[.:]{minute}(:{second})?'.format(**MACROS)




	
regexes = pd.DataFrame([
	{'regex': r'k(el)?l\s{TIME}'.format(**MACROS), 'type': 'time', 'probability': '1.0', 'example': 'kell 21:30'},
	{'regex': r'{DATE}\s*{TIME}'.format(**MACROS), 'type': 'date_time', 'probability': '0.9', 'example': '21.03.2015 15:30:45'},
	{'regex': r'{DATE}[.a ]+\s*k(el)?l\.*\s*{TIME}'.format(**MACROS), 'type': 'date_time', 'probability': '1.0', 'example':'21.03.2015. kell 15:30'},
	{'regex': r'{DATE}'.format(**MACROS), 'type': 'date', 'probability': '0.8', 'example':'12.01.98'},
	{'regex': r'{DAY}\.\s?{MONTH}'.format(**MACROS), 'type': 'partial_date', 'probability': '0.3', 'example': '03.12'},
	{'regex': r'{MONTH}\.\s?{LONGYEAR}'.format(**MACROS), 'type': 'partial_date', 'probability': '0.6', 'example': '03.2012'},
	{'regex': r'{DAY}\.\s?{MONTH}\s*k(el)?l\s{TIME}'.format(**MACROS), 'type': 'partial_date', 'probability': '0.8', 'example': '03.01 kell 10.20'},
	{'regex': r'{LONGYEAR}\s*a'.format(**MACROS), 'type': 'partial_date', 'probability': '0.8', 'example': '1998a'},
	{'regex': r'{LONGYEAR}'.format(**MACROS), 'type': 'partial_date', 'probability': '0.4', 'example': '1998'}
	]).set_index('regex')	

