class RemoveDuplicateAnalysesRewriter():
    ''' Removes duplicate analyses. 
        The analyses are duplicate if the 'root', 'ending', 'clitic', 
        'partofspeech' and 'form' attributes are equal.
        
        Returns the input list where the removals have been applied.
    '''     

    def rewrite(self, record):
        seen_analyses = set()
        to_delete = []
        for i, rec in enumerate(record):
            analysis = (rec['root'], rec['ending'], rec['clitic'], rec['partofspeech'], rec['form'])
            if analysis in seen_analyses:
                to_delete.append(i)
            else:
                seen_analyses.add(analysis)
        for i in sorted(to_delete, reverse=True):
            del record[i]

        return record
