#
#  Detects and displays *.tab duplicate file entries: 
#  lemmas with more than one possible UD conversion rule.
#

import os, os.path

if __name__ == "__main__":
    in_dir = os.getcwd()
    # Load conversion rules
    all_entries = {}
    for fname in os.listdir(in_dir):
        if fname.endswith('.tab'):
            fpath=os.path.join(in_dir, fname)
            with open( fpath, 'r', encoding='utf-8' ) as in_f:
                for line in in_f:
                    line = line.strip()
                    if len(line) > 0:
                        line_parts = line.split('\t')
                        if len(line_parts) not in [3, 4]:
                            raise ValueError(('(!) Unexpected conversion rule {!r} in file {!r}.'+\
                                              ''.format(line, fpath)))
                        vm_lemma = line_parts[0]
                        vm_lemma = (vm_lemma.replace('_', '')).replace('=', '')
                        if vm_lemma not in all_entries.keys():
                            all_entries[vm_lemma] = []
                        all_entries[vm_lemma].append( [fname, line] )
    print()
    total_duplicates = 0
    for lemma in sorted(all_entries.keys(), key=lambda x: len(all_entries[x]), reverse=True):
        entries = all_entries[lemma]
        if len(entries) > 1:
            print(f' {lemma!r} entries: {len(entries)}')
            for [fname, line] in entries:
                print('    ', [fname, line])
            total_duplicates += 1
    print()
    print('Total lemmas with multiple entries:', total_duplicates)