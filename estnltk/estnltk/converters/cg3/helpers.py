#
#   Helpful utils required for CG3 parsing
# 

import re
import sys

# ==================================================================================
#   Post-processing/clean-up steps for VISLCG3 based syntactic analysis
#   ( former 'inforemover.pl' )
#   Relocated from:
#    https://github.com/estnltk/estnltk/blob/8cb17c2d9685c9ae0498033fddde3c2f644ac200/estnltk/estnltk/taggers/syntax/vislcg3_syntax.py#L268-L377
# ==================================================================================

def cleanup_lines( lines, **kwargs ):
    ''' Cleans up annotation after syntactic pre-processing and processing:
        -- Removes embedded clause boundaries "<{>" and "<}>";
        -- Removes CLBC markings from analysis;
        -- Removes additional information between < and > from analysis;
        -- Removes additional information between " and " from analysis;
        -- If remove_caps==True , removes 'cap' annotations from analysis;
        -- If remove_clo==True , removes CLO CLC CLB markings from analysis;
        -- If double_quotes=='esc'   then "   will be overwritten with \\";
           and 
           if double_quotes=='unesc' then \\" will be overwritten with ";
        -- If fix_sent_tags=True, then sentence tags (<s> and </s>) will be
           checked for mistakenly added analysis, and found analysis will be
           removed;
        
        Returns the input list, which has been cleaned from additional information;
    '''
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    remove_caps   = False
    remove_clo    = False
    double_quotes = None
    fix_sent_tags = False
    for argName, argVal in kwargs.items() :
        if argName in ['remove_caps', 'remove_cap']:
           remove_caps = bool(argVal)
        if argName == 'remove_clo':
           remove_clo = bool(argVal)
        if argName == 'fix_sent_tags':
           fix_sent_tags = bool(argVal)
        if argName in ['double_quotes', 'quotes'] and argVal and \
           argVal.lower() in ['esc', 'escape', 'unesc', 'unescape']:
           double_quotes = argVal.lower()
    pat_token_line     = re.compile(r'^"<(.+)>"\s*$')
    pat_analysis_start = re.compile(r'^(\s+)"(.+)"(\s[LZT].*)$')
    i = 0
    to_delete = []
    while ( i < len(lines) ):
        line = lines[i]
        isAnalysisLine = line.startswith('  ') or line.startswith('\t')
        if not isAnalysisLine:
           removeCurrentTokenAndAnalysis = False
           #  1) Remove embedded clause boundaries "<{>" and "<}>"
           if line.startswith('"<{>"'):
              if i+1 == len(lines) or (i+1 < len(lines) and not '"{"' in lines[i+1]):
                 removeCurrentTokenAndAnalysis = True
           if line.startswith('"<}>"'):
              if i+1 == len(lines) or (i+1 < len(lines) and not '"}"' in lines[i+1]):
                 removeCurrentTokenAndAnalysis = True
           if removeCurrentTokenAndAnalysis:
              # Remove the current token and all the subsequent analyses
              del lines[i]
              j=i
              while ( j < len(lines) ):
                 line2 = lines[j]
                 if line2.startswith('  ') or line2.startswith('\t'):
                    del lines[j]
                 else:
                    break
              continue
           #  2) Convert double quotes (if required)
           if double_quotes:
              #  '^"<(.+)>"\s*$'
              if pat_token_line.match( lines[i] ):
                 token_cleaned = (pat_token_line.match(lines[i])).group(1)
                 # Escape or unescape double quotes
                 if double_quotes in ['esc', 'escape']:
                    token_cleaned = token_cleaned.replace('"', '\\"')
                    lines[i] = '"<'+token_cleaned+'>"'
                 elif double_quotes in ['unesc', 'unescape']:
                    token_cleaned = token_cleaned.replace('\\"', '"')
                    lines[i] = '"<'+token_cleaned+'>"'
        else:
           #  Normalize analysis line
           lines[i] = re.sub(r'^\s{4,}', '\t', lines[i])
           #  Remove clause boundary markings
           lines[i] = re.sub('(.*)" ([LZT].*) CLBC (.*)', '\\1" \\2 \\3', lines[i])
           #  Remove additional information that was added during the analysis
           lines[i] = re.sub('(.*)" L([^"<]*) ["<]([^@]*) (@.*)', '\\1" L\\2 \\4', lines[i])
           #  Remove 'cap' tags
           if remove_caps:
              lines[i] = lines[i].replace(' cap ', ' ')
           #  Convert double quotes (if required)
           if double_quotes and double_quotes in ['unesc', 'unescape']:
              lines[i] = lines[i].replace('\\"', '"')
           elif double_quotes and double_quotes in ['esc', 'escape']:
              m = pat_analysis_start.match( lines[i] )
              if m:
                 # '^(\s+)"(.+)"(\s[LZT].*)$'
                 start   = m.group(1)
                 content = m.group(2)
                 end     = m.group(3)
                 content = content.replace('"', '\\"')
                 lines[i] = ''.join([start, '"', content, '"', end])
           #  Remove CLO CLC CLB markings
           if remove_clo and 'CL' in lines[i]:
              lines[i] = re.sub(r'\sCL[OCB]', ' ', lines[i])
              lines[i] = re.sub(r'\s{2,}', ' ', lines[i])
           #  Fix sentence tags that mistakenly could have analysis (in EDT corpus)
           if fix_sent_tags:
              if i-1 > -1 and ('"</s>"' in lines[i-1] or '"<s>"' in lines[i-1]):
                 lines[i] = ''
        i += 1
    return lines


# ==================================================================================
#   Convert VISLCG format annotations to CONLL format
#   Relocated from:
#    https://github.com/estnltk/estnltk/blob/8cb17c2d9685c9ae0498033fddde3c2f644ac200/estnltk/estnltk/taggers/syntax/vislcg3_syntax.py#L380-L563
# ==================================================================================

def convert_cg3_to_conll( lines, **kwargs ):
    ''' Converts the output of VISL_CG3 based syntactic parsing into CONLL format.
        Expects that the output has been cleaned ( via method cleanup_lines() ).
        Returns a list of CONLL format lines;
        
        Parameters
        -----------
        lines : list of str
            The input text for the pipeline; Should be in same format as the output
            of VISLCG3Pipeline;

        fix_selfrefs : bool
            Optional argument specifying  whether  self-references  in  syntactic 
            dependencies should be fixed;
            Default:True
        
        fix_open_punct : bool
            Optional argument specifying  whether  opening punctuation marks should 
            be made dependents of the following token;
            Default:True
        
        unesc_quotes : bool
            Optional argument specifying  whether double quotes should be unescaped
            in the output, i.e.  converted from '\"' to '"';
            Default:True
        
        rep_spaces : bool
            Optional argument specifying  whether spaces in a multiword token (e.g. 
            'Rio de Janeiro') should be replaced with underscores ('Rio_de_Janeiro');
            Default:False
            
        error_on_unexp : bool
            Optional argument specifying  whether an exception should be raised in 
            case of missing or unexpected analysis line; if not, only prints warnings 
            in case of such lines;
            Default:False

        Example input
        --------------
        "<s>"

        "<Öö>"
                "öö" L0 S com sg nom @SUBJ #1->2
        "<oli>"
                "ole" Li V main indic impf ps3 sg ps af @FMV #2->0
        "<täiesti>"
                "täiesti" L0 D @ADVL #3->4
        "<tuuletu>"
                "tuuletu" L0 A pos sg nom @PRD #4->2
        "<.>"
                "." Z Fst CLB #5->5
        "</s>"


        Example output
        ---------------
        1       Öö      öö      S       S       com|sg|nom      2       @SUBJ   _       _
        2       oli     ole     V       V       main|indic|impf|ps3|sg|ps|af    0       @FMV    _       _
        3       täiesti täiesti D       D       _       4       @ADVL   _       _
        4       tuuletu tuuletu A       A       pos|sg|nom      2       @PRD    _       _
        5       .       .       Z       Z       Fst|CLB 4       xxx     _       _


    '''
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    fix_selfrefs   = True
    fix_open_punct = True
    unesc_quotes   = True
    rep_spaces     = False
    error_on_unexp = False
    for argName, argVal in kwargs.items() :
        if argName in ['selfrefs', 'fix_selfrefs'] and argVal in [True, False]:
           fix_selfrefs = argVal
        if argName in ['fix_open_punct'] and argVal in [True, False]:
           fix_open_punct = argVal
        if argName in ['error_on_unexp'] and argVal in [True, False]:
           error_on_unexp = argVal
        if argName in ['unesc_quotes'] and argVal in [True, False]:
           unesc_quotes = argVal
        if argName in ['rep_spaces'] and argVal in [True, False]:
           rep_spaces = argVal
    pat_empty_line    = re.compile(r'^\s+$')
    pat_token_line    = re.compile(r'^"<(.+)>"$')
    pat_analysis_line = re.compile(r'^\s+"(.+)"\s([^"]+)$')
    # 3 types of analyses: 
    pat_ending_pos_form = re.compile(r'^L\S+\s+\S\s+([^#@]+).+$')
    pat_pos_form        = re.compile(r'^\S\s+([^#@]+).+$')
    pat_ending_pos      = re.compile(r'^(L\S+\s+)?\S\s+[#@].+$')
    pat_opening_punct   = re.compile(r'.+\s(Opr|Oqu|Quo)\s')
    sentence_start = re.compile(r'^\s*$')
    analyses_added = 0
    conll_lines = []
    word_id = 1
    i = 0
    while ( i < len(lines) ):
        line = lines[i]
        # Check, whether it is an analysis line or not
        if not (line.startswith('  ') or line.startswith('\t')):
            # ******  TOKEN
            if len(line)>0 and not (line.startswith('"<s>"') and sentence_start.match(lines[i+1]) or \
               line.startswith('"</s>"')) and not pat_empty_line.match(line):
               # Convert double quotes back to normal form (if requested)
               if unesc_quotes:
                  line = line.replace( '\\"', '"' )
               # Broken stuff: if previous word was without analysis
               if analyses_added == 0 and word_id > 1:
                  # Add an empty analysis
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\tX'
                  conll_lines[-1] += '\tX'
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\t'+str(word_id-2)
                  conll_lines[-1] += '\txxx'
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\t_'
               # Start of a new token/word
               token_match = pat_token_line.match( line.rstrip() )
               if token_match:
                  word = token_match.group(1)
               else:
                  raise Exception('(!) Unexpected token format: ', line)
               if rep_spaces and re.search(r'\s', word):
                  # Replace spaces in the token with '_' symbols
                  word = re.sub(r'\s+', '_', word)
               conll_lines.append( str(word_id) + '\t' + word )
               analyses_added = 0
               word_id += 1
            # End of a sentence
            if line.startswith('"</s>"'):
                conll_lines.append('')
                word_id = 1
        else:
            analysis_match = pat_analysis_line.match( line )
            # Analysis line; in case of multiple analyses, pick the first one;
            if analysis_match and analyses_added==0:
                lemma = analysis_match.group(1)
                cats  = analysis_match.group(2)
                if cats.startswith('Z '):
                    postag = 'Z'
                else:
                    postag = (cats.split())[1] if len(cats.split())>1 else 'X'
                deprels = re.findall( r'(@\S+)', cats )
                deprel  = deprels[0] if deprels else 'xxx'
                heads   = re.findall( r'#\d+\s*->\s*(\d+)', cats )
                head    = heads[0] if heads else str(word_id-2)
                m1 = pat_ending_pos_form.match(cats)
                m2 = pat_pos_form.match(cats)
                m3 = pat_ending_pos.match(cats)
                if m1:
                    forms = (m1.group(1)).split()
                elif m2:
                    forms = (m2.group(1)).split()
                elif m3:
                    forms = ['_']  # no form (in case of adpositions and adverbs)
                else:
                    # Unexpected format of analysis line
                    if error_on_unexp:
                        raise Exception('(!) Unexpected format of analysis line: '+line)
                    else:
                        postag = 'X'
                        forms = ['_']
                        print('(!) Unexpected format of analysis line: '+line, file=sys.stderr)
                # If required, fix self-references (in punctuation):
                if fix_selfrefs and int(head) == word_id-1 and word_id-2>0:
                    head = str(word_id-2) # add link to the previous word
                # Fix opening punctuation
                if fix_open_punct and pat_opening_punct.match(line):
                    head = str(word_id)   # add link to the following word
                conll_lines[-1] += '\t'+lemma
                conll_lines[-1] += '\t'+postag
                conll_lines[-1] += '\t'+postag
                conll_lines[-1] += '\t'+('|'.join(forms))
                conll_lines[-1] += '\t'+head
                conll_lines[-1] += '\t'+deprel
                conll_lines[-1] += '\t_'
                conll_lines[-1] += '\t_'
                analyses_added += 1
        i += 1
    return conll_lines

