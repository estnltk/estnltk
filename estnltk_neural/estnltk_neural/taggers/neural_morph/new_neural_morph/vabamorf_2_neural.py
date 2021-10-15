# {vabamorf form tag : neural tag}
number_case = {'sg':'NUMBER=sg',
               'pl':'NUMBER=pl',
               'ab':'CASE=abes',
               'abl':'CASE=abl',
               'ad':'CASE=ad',
               'adt':'CASE=adit',
               'all':'CASE=all',
               'el':'CASE=el',
               'es':'CASE=es',
               'g':'CASE=gen',
               'ill':'CASE=ill',
               'in':'CASE=in',
               'kom':'CASE=kom',
               'n':'CASE=nom',
               'p':'CASE=part',
               'ter':'CASE=term',
               'tr':'CASE=tr'}
# {vabamorf partofspeech tag : neural tag}
degree_numtype = {'A':'DEGREE=pos',
                 'C':'DEGREE=comp',
                 'U':'DEGREE=super',
                 'N':'NUM_TYPE=card',
                 'O':'NUM_TYPE=ord'}
# {punctuation mark : neural tag}
punctuation = {'?':'PUNCT_TYPE=Int',
               '.':'PUNCT_TYPE=Fst',
               ':':'PUNCT_TYPE=Col',
               ',':'PUNCT_TYPE=Com',
               '(':'PUNCT_TYPE=Opr',
               ')':'PUNCT_TYPE=Cpr',
               '"':'PUNCT_TYPE=Quo',
               '“':'PUNCT_TYPE=Oqu',
               '”':'PUNCT_TYPE=Cqu',
               '[':'PUNCT_TYPE=Osq',
               ']':'PUNCT_TYPE=Csq',
               '-':'PUNCT_TYPE=Dsh',
               '!':'PUNCT_TYPE=Exc',
               ';':'PUNCT_TYPE=Scl'}

# {neural tag : [list of vabamorf form tags]}
verb_features = {'MOOD=indic':['b', 'd', 'n', 'nud', 's', 'sid', 'o', 'sime', 'sin', 'site', 'ta', 'takse', 'te', 'ti', 'vad'],
                 'MOOD=cond':['ks', 'ksid', 'ksime', 'ksin', 'ksite', 'nuks', 'nuksid', 'nuksime', 'nuksin', 'nuksite', 'taks', 'tuks'],
                 'MOOD=imper':['gu', 'ge', 'gem', 'tagu'],
                 'MOOD=quot':['vat', 'nuvat', 'tavat', 'tuvat'],

                 'VERB_FORM=inf':['da'],
                 'VERB_FORM=partic':['tud', 'tav', 'v'],
                 'VERB_FORM=sup':['ma', 'maks', 'mas', 'mast', 'mata', 'tama'],
                 'VERB_FORM=ger':['des'],

                 'VERB_PS=ps':['b', 'd', 'gu', 'ge', 'gem', 'ks', 'ksid', 'ksime', 'ksin', 'ksite', 'ma', 'maks', 'mas', 'mast', 'mata', 'me', 'n', 'ks', 'nud', 'nuks', 'vat', 'nuksid', 'nuksime', 'nuksin', 'nuksite', 'nuvat', 's', 'sid', 'sime', 'sin', 'site', 'te', 'v', 'vad', 'o'],
                 'VERB_PS=imps':['tuvat', 'tuks', 'tud', 'ti', 'tavat', 'tav', 'tama', 'takse', 'taks', 'tagu', 'ta'],

                 'VERB_POLARITY=neg':['neg', 'ta'],

                 'TENSE=pres':['b', 'd', 'gu', 'gem', 'ge', 'ks', 'ksid', 'ksime', 'ksin', 'ksite', 'me', 'n', 'vat', 'ta', 'tagu', 'taks', 'takse', 'tav', 'tavat', 'te', 'v', 'vad', 'o'],
                 'TENSE=past':['nuks', 'tud', 'nuksid', 'nuksime', 'nuksin', 'nuksite', 'nuvat', 'tuks', 'tuvat'],
                 'TENSE=impf':['nud', 's', 'sid', 'sime', 'sin', 'site', 'ti'],

                 'NUMBER=sg':['b', 'd', 'ksin', 'n', 'nuksin', 's', 'sin'],
                 'NUMBER=pl':['vad', 'te', 'site', 'sime', 'nuksite', 'nuksime', 'me', 'gem', 'ge', 'ksite', 'ksime'],

                 'PERSON=ps1':['gem', 'ksime', 'ksin', 'me', 'n', 'nuksime', 'nuksin', 'sime', 'sin'],
                 'PERSON=ps2':['d', 'ge', 'nuksite', 'ksite', 'site', 'te'],
                 'PERSON=ps3':['b', 's', 'gu', 'vad'] }

ambiguous_verb_features = {('NUMBER=sg', 'NUMBER=pl'):['ks', 'nud', 'nuks', 'nuvat', 'vat', 'o', 'gu'],
                           ('PERSON=ps1', 'PERSON=ps2', 'PERSON=ps3'):['ks', 'nud', 'nuks', 'nuvat', 'vat', 'o'],
                           ('PERSON=ps2|NUMBER=sg', 'PERSON=ps3|NUMBER=pl'):['nuksid', 'sid', 'ksid']}

def get_concatenations(analyses, tags):
    result = []
    for ana in analyses:
        for tag in tags:
            result.append(ana + '|' + tag)
    return result

def neural_model_tags(word, pos, form):
    """
    Converts vabamorf analysis into a format that is required for neural tagging.
    For example, an analysis with partofspeech: V and form: s becomes
    POS=V|MOOD=indic|TENSE=impf|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af.
    The result might be ambiguous so it returns a list of such tags.
    """
    
    if form == 'nud':
        return ['POS=V|VERB_FORM=partic|TENSE=past|VERB_PS=ps|VERB_POLARITY=af']
    if form == 'o':
        return ['POS=V|MOOD=imper|TENSE=pres|PERSON=ps2|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af']
    if word in punctuation:
        return ['POS=' + pos + '|' + punctuation[word]]

    result = 'POS=' + pos

    if form == 'me':
        result += '|MOOD=indic'
    elif form == 'neg me':
        result += '|MOOD=imper'
    elif pos in degree_numtype:
        result += '|' + degree_numtype[pos]
    form_list = form.split(' ')

    for f in form_list:
        if pos == 'V':
            for tag in verb_features:
                if f in verb_features[tag]:
                    result += '|' + tag
        elif f in number_case:
            result += '|' + number_case[f]
    if pos == 'V' and ('neg' not in result):
        result += '|VERB_POLARITY=af'

    results = [result]
    if pos == 'V':
        for f in form_list:
            for tags in ambiguous_verb_features:
                if f in ambiguous_verb_features[tags]:
                    results = get_concatenations(results, tags)
    if form == 'neg o':
        results.append('POS=V|MOOD=imper|TENSE=pres|PERSON=ps2|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=neg')
    elif form == 'neg gu':
        results.append('POS=V|MOOD=imper|TENSE=pres|VERB_PS=imps|VERB_POLARITY=neg')
    return results