import codecs
import regex

def test_abileksikon():
    nonSpacePattern = regex.compile('^\S+$')
    posTagPattern   = regex.compile('_._')
    file = '../syntax_preprocessing/rules_files/abileksikon06utf.lx'
    
    roots = set()
    in_f = codecs.open(file, mode='r', encoding='utf-8')
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
            premise, tags = l.split('>')
            premise = premise.strip()
            assert premise not in premises, 'repetitive premise on line number {}: "{}"'.format(line_number, line.rstrip())
            premises.add(premise)
            if premise not in {'_Y_', '_Z_'}:
                assert all(tag.strip('|').startswith('#') for tag in tags.split()), 'missing # on line number {}: "{}"'.format(line_number, line.rstrip())