#
# Patches to be applied before processing a string with Bert
#

def estbert_normalizer( input_str ):
    '''Fixes obscure string combinations on which the EstBert model fails 
       to generate embeddings and throws an Exception (an `IndexError`) instead. 
       Currently known problematic cases are related to non-space char combinations 
       with specific cyrillic letters, e.g. '4e' or 'Sи'.
    '''
    len_before_replace = len(input_str)
    input_str = input_str.replace("\u0435", "e") # Replace cyrillic 'e' with the ASCII 'e'
    input_str = input_str.replace("\u0438", "i") # Replace cyrillic 'и' with the ASCII 'i'
    assert len(input_str) == len_before_replace
    return input_str