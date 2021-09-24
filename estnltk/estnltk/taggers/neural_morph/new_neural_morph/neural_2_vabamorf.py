# {vabamorf form tag : neural tag}
number = {'sg':'NUMBER=sg',
          'pl':'NUMBER=pl'}

case = {'ab':'CASE=abes',
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
                 'O':'NUM_TYPE=ord',
                 'J':'POS=SCONJ'}

# This table of verb (POS=V) features assumes that there will be no 'neg' tag.
pos_verb_features = {'da':{'VERB_FORM=inf'},
                 'des':{'VERB_FORM=ger'},
                 
                 'ma':{'VERB_FORM=sup', 'CASE=ill'},
                 'maks':{'VERB_FORM=sup', 'CASE=tr'},
                 'mas':{'VERB_FORM=sup', 'CASE=in'},
                 'mast':{'VERB_FORM=sup', 'CASE=el'},
                 'mata':{'VERB_FORM=sup', 'CASE=abes'},
                 'tama':{'VERB_FORM=sup', 'VERB_PS=imps'},
                 
                 'n':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=sg', 'VERB_PS=ps'},
                 'd':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=sg', 'VERB_PS=ps'},
                 'b':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps3', 'NUMBER=sg', 'VERB_PS=ps'},
                 'me':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps'},
                 'te':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=pl', 'VERB_PS=ps'},
                 'vad':{'MOOD=indic', 'TENSE=pres', 'PERSON=ps3', 'NUMBER=pl', 'VERB_PS=ps'},
                 
                 's':{'MOOD=indic', 'TENSE=impf', 'PERSON=ps3', 'NUMBER=sg', 'VERB_PS=ps'},
                 'sid':[{'MOOD=indic', 'TENSE=impf', 'PERSON=ps2', 'NUMBER=sg', 'VERB_PS=ps'},
                        {'MOOD=indic', 'TENSE=impf', 'PERSON=ps3', 'NUMBER=pl', 'VERB_PS=ps'}],
                 'sime':{'MOOD=indic', 'TENSE=impf', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps'},
                 'sin':{'MOOD=indic', 'TENSE=impf', 'PERSON=ps1', 'NUMBER=sg', 'VERB_PS=ps'},
                 'site':{'MOOD=indic', 'TENSE=impf', 'PERSON=ps2', 'NUMBER=pl', 'VERB_PS=ps'},
                 
                 'ksid':[{'MOOD=cond', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=sg', 'VERB_PS=ps'},
                         {'MOOD=cond', 'TENSE=pres', 'PERSON=ps3', 'NUMBER=pl', 'VERB_PS=ps'}],
                 'ksime':{'MOOD=cond', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps'},
                 'ksin':{'MOOD=cond', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=sg', 'VERB_PS=ps'},
                 'ksite':{'MOOD=cond', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=pl', 'VERB_PS=ps'},
                 
                 'nuksid':[{'MOOD=cond', 'TENSE=past', 'PERSON=ps2', 'NUMBER=sg', 'VERB_PS=ps'},
                           {'MOOD=cond', 'TENSE=past', 'PERSON=ps3', 'NUMBER=pl', 'VERB_PS=ps'}],
                 'nuksime':{'MOOD=cond', 'TENSE=past', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps'},
                 'nuksin':{'MOOD=cond', 'TENSE=past', 'PERSON=ps1', 'NUMBER=sg', 'VERB_PS=ps'},
                 'nuksite':{'MOOD=cond', 'TENSE=past', 'PERSON=ps2', 'NUMBER=pl', 'VERB_PS=ps'},
                 
                 'o':{'MOOD=imper', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=sg', 'VERB_PS=ps', 'VERB_POLARITY=af'},
                 'tagu':{'MOOD=imper', 'TENSE=pres', 'VERB_PS=imps'},
                 
                 'ta':{'MOOD=indic', 'TENSE=pres', 'VERB_PS=imps', 'VERB_POLARITY=neg'},
                 'takse':{'MOOD=indic', 'TENSE=pres', 'VERB_PS=imps', 'VERB_POLARITY=af'},
                 'ti':{'MOOD=indic', 'TENSE=impf', 'VERB_PS=imps'},
                 
                 'taks':{'MOOD=cond', 'TENSE=pres', 'VERB_PS=imps'},
                 'tuks':{'MOOD=cond', 'TENSE=past', 'VERB_PS=imps'},
                 
                 'nuvat':{'MOOD=quot', 'TENSE=past', 'VERB_PS=ps'},
                 'tuvat':{'MOOD=quot', 'TENSE=past', 'VERB_PS=imps'},
                 'tavat':{'MOOD=quot', 'TENSE=pres' 'VERB_PS=imps'},
                 
                 'tav':{'VERB_FORM=partic', 'TENSE=pres', 'VERB_PS=imps'},
                 'v':{'VERB_FORM=partic', 'TENSE=pres', 'VERB_PS=ps'},
                 'nud':{'VERB_FORM=partic', 'TENSE=past', 'VERB_PS=ps'}}

# These verb tags can have 'neg' attached in front if there is VERB_POLARITY=neg in the morphtag.
pos_neg_verb_features = {'tud':{'VERB_FORM=partic', 'TENSE=past', 'VERB_PS=imps'},
                         'vat':{'MOOD=quot', 'TENSE=pres', 'VERB_PS=ps'},
                         'nuks':{'MOOD=cond', 'TENSE=past', 'VERB_PS=ps'},
                         'ks':{'MOOD=cond', 'TENSE=pres', 'VERB_PS=ps'},
                         'ge':{'MOOD=imper', 'TENSE=pres', 'PERSON=ps2', 'NUMBER=pl', 'VERB_PS=ps'},
                         'gem':{'MOOD=imper', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps'},
                         'gu':{'MOOD=imper', 'TENSE=pres', 'PERSON=ps3', 'VERB_PS=ps'}}

# These verb tags ďon't fit into previous categories.
neg_verb_features = {'neg me':{'MOOD=imper', 'TENSE=pres', 'PERSON=ps1', 'NUMBER=pl', 'VERB_PS=ps', 'VERB_POLARITY=neg'},
                     'neg nud':{'MOOD=indic', 'TENSE=impf', 'VERB_PS=ps', 'VERB_POLARITY=neg'}}

def iterate(tag_dict, morphtags):
    for form in tag_dict:
        if isinstance(tag_dict[form], list):
            for tag_set in tag_dict[form]:
                if tag_set.issubset(morphtags):
                    return form
        else:
            if tag_dict[form].issubset(morphtags):
                return form
        
    return None

def vabamorf_tags(morphtag, postfix=True):
    """
    Converts a morphtag from neural model into vabamorf format.
    
    Parameters:
    
    postfix: boolean
        Applies postfixes to ensure correct Vabamorf tags.
    """
    morphtags = morphtag.split('|')
    pos = morphtags[0].split('=')[1]
    morphtags = set(morphtags)
    
    if pos == 'V':
        form = iterate(pos_verb_features, morphtags)
        
        if form is None:
            form = iterate(pos_neg_verb_features, morphtags)
            if form is not None:
                if 'VERB_POLARITY=neg' in morphtags:
                    return pos, 'neg ' + form
                return pos, form
            
            form = iterate(neg_verb_features, morphtags)
            if form is not None:
                return pos, form
            
            return pos, 'neg'
        
        return pos, form
    
    form = ''
    for num_form in number:
        if number[num_form] in morphtags:
            form = num_form
    for case_form in case:
        if case[case_form] in morphtags:
            form += ' ' + case_form
    for pos_tag in degree_numtype:
        if degree_numtype[pos_tag] in morphtags:
            pos = pos_tag
    
    if postfix:
        # Correct postag for proper names
        if pos == 'S' and 'NOUN_TYPE=prop' in morphtags:
            pos = 'H'
        # Correct 'adt' form
        if form == 'sg adt':
            form = 'adt'
    return pos, form
    
    
    
        