import regex
from os.path import dirname, join

import estnltk.taggers.standard.syntax.preprocessing as syntax_pp

def test_abileksikon():
    nonSpacePattern = regex.compile(r'^\S+$')
    posTagPattern   = regex.compile('_._')
    file = join(dirname(syntax_pp.__file__), 'rules_files', 'abileksikon06utf.lx')
    # not sure if this set is complete
    hashtags = {'#Abl', '#Ad', '#All', '#El', '#Es', '#Ill', '#In', '#Inf',
                '#InfP', '#Int', '#Intr', '#Kom', '#NGP', '#NGP-P', '#Part',
                '#Part-P', '#Ter', '#Tr', '#abes', '#all', '#el', '#gen',
                '#kom', '#nom', '#part', '#term'}
    roots = set()
    with open(file, mode='r', encoding='utf_8') as in_f:
        line_number = 0
        while True:
            line = next(in_f, None)
            line_number += 1
            if line == None:
                break
            assert nonSpacePattern.match(line), 'whitespace in root: "' + line +'"'
            line = line.rstrip()
            assert line not in roots, 'repetitive root: "' + line + '"'
            roots.add(line)
        
            line = next(in_f, None)
            line_number += 1
            assert line != None, 'odd number of lines in file'
            premises = set()
            for l in line.split('&'):
                l = l.strip()
                assert posTagPattern.match(l), 'incorrect pos format on line number {}: "{}"'.format(line_number, line.rstrip())
                # not sure if this set is complete
                assert l[1] in {'K', 'V', 'Y', 'Z'}, 'unexpected pos "{}" on line number {}: "{}"'.format(l[1], line_number, line.rstrip())
                lsplit = l.split('>')
                assert len(lsplit) == 2, 'missing or extra > on line number {}: "{}"'.format(line_number, line.rstrip())
                premise, tags = lsplit
                premise = premise.strip()
                assert premise not in premises, 'repetitive premise on line number {}: "{}"'.format(line_number, line.rstrip())
                premises.add(premise)
                if premise not in {'_Y_', '_Z_'}:
                    for tag in tags.split():
                        tag = tag.strip('|')
                        assert tag.startswith('#'), 'missing # on line number {}: "{}"'.format(line_number, line.rstrip())
                        assert tag in hashtags, 'unexpected hashtag "{}" on line number {}: "{}"'.format(tag, line_number, line.rstrip())