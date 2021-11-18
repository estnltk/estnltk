from os.path import dirname, join

import estnltk.taggers.standard.syntax.preprocessing as syntax_pp


# not sure if the following sets are complete
pos0 = {'####', '_A_', '_C_', '_D_', '_G_', '_H_', '_I_', '_J_', '_K_',
        '_N_', '_O_', '_P_', '_S_', '_U_', '_V_', '_X_', '_Y_', '_Z_'}
pos1 = {'_A_', '_D_', '_G_', '_I_', '_J_', '_K_', '_N_', '_P_', '_S_', 
        '_T_', '_V_', '_X_', '_Y_', '_Z_'}
form0 = {'?', 'ab', 'abl', 'ad', 'adt', 'all', 'b', 'd', 'da', 'des', 'el',
         'es', 'g', 'ge', 'gem', 'gu', 'ill', 'in', 'kom', 'ks', 'ksid',
         'ksime', 'ksin', 'ksite', 'ma', 'maks', 'mas', 'mast', 'mata', 'me',
         'n', 'neg', 'nud', 'nuks', 'nuksid', 'nuksime', 'nuksin', 'nuksite',
         'nuvat', 'o', 'p', 'pl', 's', 'sg', 'sid', 'sime', 'sin', 'site',
         'ta', 'tagu', 'taks', 'takse', 'tama', 'tav', 'tavat', 'te', 'ter',
         'ti', 'tr', 'tud', 'tuks', 'tuvat', 'v', 'vad', 'vat'}
form1 = {'?', 'Col', 'Com', 'Cpr', 'Cqu', 'Csq', 'Dsd', 'Dsh', 'Ell', 'Els',
         'Exc', 'Fst', 'Int', 'Opr', 'Oqu', 'Osq', 'Quo', 'Scl', 'Sla', 'abes',
         'abl', 'ad', 'adit', 'adjectival', 'adverbial', 'af', 'all', 'aux',
         'card', 'com', 'comp', 'cond', 'crd', 'digit', 'el', 'es', 'gen',
         'ger', 'ill', 'imper', 'impf', 'imps', 'in', 'indic', 'inf', 'kom',
         'l', 'main', 'mod', 'neg', 'nom', 'nominal', 'ord', 'part', 'partic',
         'past', 'pl', 'pos', 'post', 'pre', 'pres', 'prop', 'ps', 'ps1',
         'ps2', 'ps3', 'quot', 'roman', 'sg', 'sub', 'sup', 'super', 'term',
         'tr', 'verbal'}

def test_tmorftrtabel():
    """ Checks the format of tmorftrtabel.txt lines. Includes the lines that
    are marked to be skipped ('¤' in the beginning).
    """
    file = join(dirname(syntax_pp.__file__), 'rules_files', 'tmorftrtabel.txt')
    with open(file, mode='r', encoding='utf_8') as in_f:
        for line_number, line in enumerate(in_f):
            line_number += 1
            # ei nori realõpu tühikute kallal
            line = line.rstrip()
            parts = line.lstrip('¤').split('@')
            assert len(parts) == 8, 'wrong number of "@" on line number {}: "{}"'.format(line_number, line)
            for part in parts:
                assert part == part.strip(), 'extra space on line number {}: "{}"'.format(line_number, line) 
            p_split = parts[1].split(' ')
            assert p_split[0] in pos0, 'unexpected form pos tag "{}" on line number {}: "{}"'.format(p_split[0], line_number, line)
            assert set(p_split[1:]) < form0, 'unexpected for tag "{}" on line number {}: "{}"'.format(set(p_split[1:])-form0, line_number, line)
            p_split = parts[3].split(' ')
            assert p_split[0] in pos1, 'unexpected form pos tag "{}" on line number {}: "{}"'.format(p_split[0], line_number, line)
            assert set(p_split[1:]) < form1, 'unexpected for tag {} on line number {}: "{}"'.format(set(p_split[1:])-form1, line_number, line)