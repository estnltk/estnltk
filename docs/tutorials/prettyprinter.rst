==================
HTML Prettyprinter
==================
.. highlight:: python
.. raw:: html

Visualizing information is one of the most crucial steps in text processing software and arises in many uses cases.
Estnltk comes with HTML PrettyPrinter that can help building Web applications and custom tools that deal with
text processing.

PrettyPrinter is capable of very different types of visualization. From  visualization of simple given word to multiple
and overlapping word types and even parts of whole sentences.


Example #1 formating specific word

from ...text import Text
from ..prettyprinter import PrettyPrinter

text = Text('This must be formatted here and here')
text.tag_with_regex('annotations', 'here')

pp = PrettyPrinter(background='annotations')
print(pp.render(text, True))

The result of this short program will be:
<embed>
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>

      mark.background_0 {
            background-color: rgb(102, 204, 255);
            }
    </style>
    <body>
        <p>
            This must be formated <mark class="background_0">here</mark> and <mark class="background_0">here</mark>
        </p>
    </body>
</html>
</embed>

Class Text('...') is what does all the analysis. If we are looking to mark a specific word as in this case is the word
"here" then we must bind the annotation to the word "here" with the help of a function of Text('...') called
tags_with_regex('annotations', 'here') that tags the value of 'annotations' to the word 'here'. This will later be used
to find the exact index where to start and end the selected formating.

When we create a new class PrettyPrinter variable by "pp = PrettyPrinter(background='annotations')", we add arguments
describing what property will be added to which tag, in our case, everything that is tagged as 'annotations' will get a
different background color. The rgb(102, 204, 255) is a stock value that is added as background color if no other color
is specified during initiation of the PrettyPrinter class object.

... content ...

