class LetterCaseRewriter():
    ''' The 'letter_case' attribute gets the value
            'cap' if the word has capital beginning
            None otherwise
    '''
    
    def rewrite(self, record):
        if record and record[0]['text'][0].isupper():
            cap = 'cap'
        else:
            cap = None
        for rec in record:
            rec['letter_case'] = cap
        return record
