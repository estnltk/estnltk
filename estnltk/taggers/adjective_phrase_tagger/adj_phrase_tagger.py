from copy import copy

from estnltk import Text

from .adverbs import NOT_ADJ_MODIFIERS, CLASSES, WEIGHTS
from .grammars import adjective_phrases, part_phrase
from .measurement_adjectives import is_measurement_adjective


class AdjectivePhraseTagger:
    def __init__(self, return_layer=False, layer_name='adjective_phrases'):
        """
        Tags adjective phrases
        Parameters
        ----------
        return_layer_only - do not annotate the text object, return just the resulting layer
        layer_name - the name of the layer. Does nothing when return_layer_only is set
        """
        self.layer_name = layer_name
        self.return_layer = return_layer


    def __extract_lemmas(self, doc, m, phrase):
        """
        :param sent: sentence from which the match was found
        :param m: the found match
        :phrase: name of the phrase
        :return: tuple of the lemmas in the match
        """

        ph_start = m['start']
        ph_end = m['end']
        start_index = None
        for ind, word in enumerate(doc['words']):
            if word['start'] == ph_start:
                start_index = ind
                break
        end_index = None
        for ind, word in enumerate(doc['words']):
            if word['end'] == ph_end:
                end_index = ind
                break
        if start_index is not None and end_index is not None:
            
            lem = []
                
            for i in doc['words'][start_index:end_index + 1]:
                word_lem = []
                for idx, j in enumerate(i['analysis']):
                    if i['analysis'][idx]['partofspeech'] in ['A', 'D', 'C', 'J']:
                        if i['analysis'][idx]['lemma'] not in word_lem:
                            word_lem.append(i['analysis'][idx]['lemma'])
                word_lem_str = '|'.join(word_lem)          
                lem.append(word_lem_str)

        else:
            raise Exception('Something went really wrong')
        return lem



    # Tags (normal) adjective phrases and comparative phrases in text, adds lemmas and type (adjective or comparative)
    def __tag_adj_phrases(self, text):
        adjective_phrases.name = self.layer_name
        adjective_phrases.annotate(text)
        if self.layer_name in text:
            for idx, adj_ph in enumerate(text[self.layer_name]):
                phrase_lemmas = self.__extract_lemmas(text, text[self.layer_name][idx], self.layer_name)
                #adj_ph['lemmas'] = Text(adj_ph['text'], disambiguate=False).lemmas
                adj_ph['lemmas'] = phrase_lemmas
                
                if 'C' in Text(adj_ph['lemmas'][-1]).postags:
                    adj_ph['type'] = 'comparative'
                else:
                    adj_ph['type'] = 'adjective'
                    
                if len(adj_ph['lemmas']) > 1:
                    if adj_ph['lemmas'][0] in CLASSES:
                        adj_ph['adverb_class'] = CLASSES[adj_ph['lemmas'][0]]
                        adj_ph['adverb_weight'] = WEIGHTS[adj_ph['adverb_class']]
                    else:
                        adj_ph['adverb_class'] = 'unknown'
                    
                if len(adj_ph['lemmas']) == 4:
                    if self.__is_ja_phrase(adj_ph['text']):
                        pass
                    else:
                        text[self.layer_name][idx]['to_delete'] = True

        return text


    def __is_ja_phrase(self, phrase):
        phrase = phrase.split()
        adj_1_forms = Text(phrase[1]).forms
        adj_2_forms = Text(phrase[3]).forms
        for form in adj_1_forms:
            for form2 in adj_2_forms:
                if form == form2:
                    return True
        return False


    # Checks whether the adverb-adjective sequence tagged as participle phrase can actually be one
    def __is_participle_phrase(self, lemmas):
        # If the last element of the lemma gets the verb POS tag and ends with v/tav/nud/tud, the word is a participle
        for lemma in lemmas.split('|'):
            last_token = Text(lemma, disambiguate=False).roots[0].split('_')[-1]
            for token in last_token.split('|'):
                if 'V' in Text(token, disambiguate=False).postags[0].split('|'):
                    if lemma[-1] == 'v' or (lemma[-1] == 'd' and lemma[-2] == 'u'):
                        return True


    # Tags participle phrases, adds lemmas and type (participle)
    def __tag_participle_phrases(self, text):
        part_phrase.annotate(text)
        if 'participle_phrases' in text:
            for idx, part_ph in enumerate(text['participle_phrases']):
                #part_ph['lemmas'] = Text(part_ph['text'], disambiguate=False).lemmas
                phrase_lemmas = self.__extract_lemmas(text, text['participle_phrases'][idx], 'participle_phrases')
                part_ph['lemmas'] = phrase_lemmas
                if self.__is_participle_phrase(part_ph['lemmas'][1]):
                    part_ph['type'] = 'participle'
                    if part_ph['lemmas'][0] in NOT_ADJ_MODIFIERS:
                        pass
                    else:
                        if len(part_ph['lemmas']) > 1:
                            if part_ph['lemmas'][0] in CLASSES:
                                part_ph['adverb_class'] = CLASSES[part_ph['lemmas'][0]]
                                part_ph['adverb_weight'] = WEIGHTS[part_ph['adverb_class']]
                            else:
                                part_ph['adverb_class'] = 'unknown'  
                        
                        if self.layer_name in text:
                            for idx, adj_ph in enumerate(text[self.layer_name]):
                                # If participle phrase was also (partially) tagged as a usual adjective phrase, the latter is removed
                                if adj_ph['end'] == part_ph['end'] or adj_ph['start'] == part_ph['start']:
                                    text[self.layer_name][idx]['to_delete'] = True
                                  
                                    
                            # Participle phrases included into adjective_phraes layer
                            text[self.layer_name].append(part_ph)
                        else:
                            text[self.layer_name] = []
                            text[self.layer_name].append(part_ph)
            del text['participle_phrases']
        return text


    # Removes tagged phrases starting with "nii" and followed by "kui" ("nii juriidilised kui majanduslikud põhjused...")
    def __remove_nii_kui_phrase(self, sent):
        for idx, adj_ph in enumerate(sent[self.layer_name]):
            if adj_ph['lemmas'][0] == 'nii':
                for i in sent['words']:
                    if i['start'] == adj_ph['end'] + 1:
                        if (i['analysis'][0]['lemma'] == 'kui' or i['analysis'][0]['partofspeech'] == 'A'):
                            sent[self.layer_name][idx]['to_delete'] = True
        return sent


    # Finds if tagged phrase intersects with verb chains - in case of participles,
    # this mostly means that the tagged phrase is not an actual adjective phrase
    def __adj_verb_intersections(self, start, end, sent):
        sent.verb_chains
        for verb_ph in sent['verb_chains']:
            for start_v, end_v in zip(verb_ph['start'], verb_ph['end']):
                if end_v <= end and end_v >= start:
                    return True
                elif start_v >= start and start_v <= end:
                    return True
        else:
            return False
            

    # Deletes phrases marked as 'to_delete'
    def __delete_wrong_phrases(self, text):
        correct_adj_phrases = []
        for ph in text[self.layer_name]:
            if 'to_delete' in ph:
                pass
            else:
                correct_adj_phrases.append(ph)
        text[self.layer_name] = correct_adj_phrases
        return text


    ###################################
    def tag(self, text):
        if self.return_layer:
            t2 = copy(text)
            a2 = AdjectivePhraseTagger()
            a2.tag(t2)
            
            try:
                return t2[a2.layer_name]
            except KeyError:
                return []  
            
        else:
            if self.layer_name in text:
                return text

            else:
                text = self.__tag_adj_phrases(text)
                text = self.__tag_participle_phrases(text)
                if self.layer_name in text:
                    for idx, adj_ph in enumerate(text[self.layer_name]):
                        adj_ph = (dict(adj_ph))
                        # Finds whether the adjective is a measurement adjective
                        if is_measurement_adjective(adj_ph['lemmas'][-1]) == True:
                            text[self.layer_name][idx]['measurement_adj'] = True
                        else:
                            text[self.layer_name][idx]['measurement_adj'] = False

                        if self.__adj_verb_intersections(adj_ph['start'], adj_ph['end'], text) == True:
                            text[self.layer_name][idx]['intersects_with_verb'] = True
                        else:
                            text[self.layer_name][idx]['intersects_with_verb'] = False
                    text = self.__remove_nii_kui_phrase(text)
                    text = self.__delete_wrong_phrases(text)
                return text
