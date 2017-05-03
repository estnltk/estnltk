from estnltk.tokenizers.word_tokenizer import tri_rules, bi_rules, apply_rules
import estnltk.text
import estnltk
import re

EMOTICONS = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
      |
      <3                         # heart
    )"""


URLS = r"""			# Capture 1: entire matched URL
  (?:
  https?:				# URL protocol and colon
    (?:
      /{1,3}				# 1-3 slashes
      |					#   or
      [a-z0-9%]				# Single letter or digit or '%'
                                       # (Trying not to match e.g. "URI::Escape")
    )
    |					#   or
                                       # looks like domain name followed by a slash:
    [a-z0-9.\-]+[.]
    (?:[^\W\d_]{2,13})
    /
  )
  (?:					# One or more:
    [^\s()<>{}\[\]]+			# Run of non-space, non-()<>{}[]
    |					#   or
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)				# balanced parens, non-recursive: (...)
  )+
  (?:					# End with:
    \([^\s()]*?\([^\s()]+\)[^\s()]*?\) # balanced parens, one level deep: (...(...)...)
    |
    \([^\s]+?\)				# balanced parens, non-recursive: (...)
    |					#   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]	# not a space or one of these punct chars
  )
  |					# OR, the following to match naked domains:
  (?:
  	(?<!@)			        # not preceded by a @, avoid matching foo@_gmail.com_
    [a-z0-9]+
    (?:[.\-][a-z0-9]+)*
    [.]
    (?:[a-z]{2,13})
    \b
    /?
    (?!@)			        # not succeeded by a @,
                            # avoid matching "foo.na" in "foo.na@example.com"
  )
"""

# The components of the tokenizer:
REGEXPS = (
    URLS,
    # ASCII Emoticons
    EMOTICONS
    ,
    #emails
    r"""[^@\s]+@[^@\s]+\.[^@\s]+"""
    ,
    # HTML tags:
    r"""<[^>\s]+>"""
    ,
    # ASCII Arrows
    r"""[\-]+>|<[\-]+"""
    ,
    # hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,

    # Remaining word types:
    r"""
    (?:[^\W\d_][\d'_]+[^\W\d_])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
)

######################################################################
# This is the core tokenizing regex:

WORD_RE = re.compile(r"""(%s)""" % "|".join(REGEXPS), re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can preserve case for
# them as needed:
EMOTICON_RE = re.compile(EMOTICONS, re.VERBOSE | re.I | re.UNICODE)



######################################################################

class CasualTokenizer:
    def __init__(self, preserve_case=True, reduce_len=False, strip_handles=False):
        self.preserve_case = preserve_case
        self.reduce_len = reduce_len
        self.strip_handles = strip_handles

    def _tokenize(self, text):
        spans = [i.span() for i in re.finditer(WORD_RE, text)]
        tokens = [text[s:e] for s, e in spans]
        tokens, spans = apply_rules(tokens, spans, 3, tri_rules)
        tokens, spans = apply_rules(tokens, spans, 2, bi_rules)
        return tokens, spans



    def tokenize(self, text):
        """
        :param text: str
        :rtype: list(str)
        :return: a tokenized list of strings; concatenating this list returns\
        the original string if `preserve_case=False`
        """
        return self._tokenize(text)[0]

    def span_tokenize(self, text):
        return self._tokenize(text)[1]

####################################################################################################
t = 'Minu nimi on Uku :)http://www.nltk.org/api/nltk.tokenize.html 1,2,3 1:10 teine. mina@gmail.com, uku.raudvere@ut.ee'
print(estnltk.Text(t).lemmas)
estnltk.text.word_tokenizer = CasualTokenizer()
print(estnltk.Text(t).lemmas)

