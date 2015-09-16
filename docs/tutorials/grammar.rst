==========================================
Simple grammars for information extraction
==========================================
.. highlight:: python

Estnltk comes with simple grammar constructs that are useful for basic information extraction.
Consider that you have a recipe for making panncakes::

    recipe = '''
    2,5 dl piima
    1,5 dl jahu
    1 muna
    1 tl suhkrut
    1 tl vaniljeekstrakti
    0,5 tl soola
    '''

Suppose you want to create a robot that can cook various meals.
In order to program that robot, you need a software module, which can parse recipes.
This is where Estnltk's ``estnltk.grammar.grammar`` module can help you.

In the above example, we need to parse the numbers, unit and the name of the ingredient
into more managenable form than free-text::

    from estnltk import Regex, Lemmas

    number = Regex('\d+([,.]\d+)?', name='amount')
    unit = Lemmas('dl', 'tl', name='unit')
    ingredient = Lemmas('piim', 'jahu', 'muna', 'suhkur', 'vaniljeekstrakt', 'sool', name='ingredient')

Now, there are two types of instructions::

    from estnltk import Concatenation

    space = Regex('\s*')
    full_instruction = Concatenation(number, unit, ingredient, sep=space)
    short_instruction = Concatenation(number, ingredient, sep=space)

And we want to capture them both::

    from estnltk import Union

    instruction = Union(full_instruction, short_instruction, name='instruction')

Basically, a grammar contains a number of symbols that can be chained together in various ways
and rigged for information extraction.
Above grammar just extracts numbers defined by a regular expression, and units and ingredients
based on user given lists.

Now, going back to our robot example, we can extract the data from text using ``get_matches`` method::

    from estnltk import Text
    from pprint import pprint

    text = Text(recipe)
    for match in instruction.get_matches(text):
        pprint(match.dict)


The ``dict`` attribute of each :py:class:`~estnltk.grammar.match.Match` instance can be used
to access the symbol's name, matched text, start and end positions and also all submatches::

    {'amount': {'end': 4, 'start': 1, 'text': '2,5'},
     'ingredient': {'end': 13, 'start': 8, 'text': 'piima'},
     'instruction': {'end': 13, 'start': 1, 'text': '2,5 dl piima'},
     'unit': {'end': 7, 'start': 5, 'text': 'dl'}}
    ...
     'ingredient': {'end': 80, 'start': 75, 'text': 'soola'},
     'instruction': {'end': 80, 'start': 68, 'text': '0,5 tl soola'},
     'unit': {'end': 74, 'start': 72, 'text': 'tl'}}


You can also use the symbols to tag layers directly in :py:class:`~estnltk.text.Text` instances::

    instruction.annotate(text)

Let's use prettyprinter to visualize this as HTML::

    from estnltk import PrettyPrinter
    pp = PrettyPrinter(background='instruction', underline='ingredient', weight='unit')
    pp.render(text, add_header=True)


.. raw:: html

    <style>
        mark.background {
            background-color: rgb(102, 204, 255);
        }
        mark.weight {
            font-weight: bold;
        }
        mark.underline {
            text-decoration: underline;
        }
    </style>
    <mark class="background">2,5 </mark><mark class="background weight">dl</mark><mark class="background"> </mark><mark class="background underline">piima</mark><br/><mark class="background">1,5 </mark><mark class="background weight">dl</mark><mark class="background"> </mark><mark class="background underline">jahu</mark><br/><mark class="background">1 </mark><mark class="background underline">muna</mark><br/><mark class="background">1 </mark><mark class="background weight">tl</mark><mark class="background"> </mark><mark class="background underline">suhkrut</mark><br/><mark class="background">1 </mark><mark class="background weight">tl</mark><mark class="background"> </mark><mark class="background underline">vaniljeekstrakti</mark><br/><mark class="background">0,5 </mark><mark class="background weight">tl</mark><mark class="background"> </mark><mark class="background underline">soola</mark><br/>

You can access the annotated layers as you would access typical layers::

    print(text['ingredient'])

::

    [{'end': 13, 'start': 8, 'text': 'piima'},
     {'end': 25, 'start': 21, 'text': 'jahu'},
     {'end': 32, 'start': 28, 'text': 'muna'},
     {'end': 45, 'start': 38, 'text': 'suhkrut'},
     {'end': 67, 'start': 51, 'text': 'vaniljeekstrakti'},
     {'end': 80, 'start': 75, 'text': 'soola'}]


See package ``estnltk.grammar.examples`` for more examples.
