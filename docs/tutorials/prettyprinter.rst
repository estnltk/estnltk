==================
HTML Prettyprinter
==================
.. highlight:: python
.. raw:: html

Visualizing information is one of the most crucial steps in text processing software and arises in many uses cases.
Estnltk comes with HTML PrettyPrinter that can help building Web applications and custom tools that deal with
text processing.

PrettyPrinter is capable of very different types of visualization. From  visualization of simple given word to multiple
and overlapping word types and even parts of whole sentences. Here is a list of porperties that can be modified with the
help of PrettyPrinter and the matching name of the value that the module is expecting:

    Change font color - 'color'
    Change background color - 'background'
    Change font style - 'font'
    Change font weight - 'weight'
    Change font style - 'italics'
    Add underline - 'underline'
    Change font size - 'size'
    Change letter spacing - 'tracking'


Example #1 Formating specific word in all of text with different visual format.

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

      mark.background{
            background-color: rgb(102, 204, 255);
            }
    </style>
    <body>
        <p>
            This must be formated <mark class="background">here</mark> and <mark class="background">here</mark>
        </p>
    </body>
</html>
</embed>

Class Text('...') is what does all the analysis. If we are looking to mark a specific word as in this case is the word
'here' then we must bind the annotation to the word 'here' with the help of a function of Text('...') called
tags_with_regex('annotations', 'here') that tags the value of 'annotations' to the word 'here'. This will later be used
to find the exact index where to start and end the selected formating.

When we create a new class PrettyPrinter variable by 'pp = PrettyPrinter(background='annotations')', we add arguments
describing what property will be added to which tag, in our case, everything that is tagged as 'annotations' will get a
different background color. The rgb(102, 204, 255) is a stock value that is added as background color if no other color
is specified during initiation of the PrettyPrinter class object.

Keep in mind that if we activate PrettyPrinter function with the argument 'False' instead of 'True', then the result
will not be the full HTML text, but only the formatted text inside the HTML body paragraph.

Example #2 Formating the same property with different visual format depending on the specific word

text = Text('Nimisõnad värvitakse').tag_analysis()
rules =[
            ('Nimisõnad', 'green'),
            ('värvitakse', 'blue')
        ]
pp = PrettyPrinter(background='words', background_value=rules)
html = pp.render(text, True)

The result of this program will be:

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
            background-color: green;
        }
        mark.background_1 {
            background-color: blue;
        }

    </style>
    <body>

<mark class="background_0">Nimisõnad</mark> <mark class="background_1">värvitakse</mark>
    </body>
</html>
</embed>

This time we gave the PrettyPrinter class object two arguments: background='words', background_value=rules. The background
value 'words' means that we will not be adding any specific tags as in the previous case, but instead use the original
tag that is used in case of every word. PrettyPrinter will check itself what words match the rules specified in the list
'rules'. Now the second argument background_value=rules shows PrettyPrinter what values will be given to what tag values.
Basically what our 'rules' say to the PrettyPrinter is that each word 'Nimisõnad' will be given a green background
color and the word 'värvitakse' will be given a blue background color. Because different words can have different visual
properties of the same type(eg. background color, font color, font size etc.) the css marks are numbered based on the
number of overlapping values.

Example #3 Using word type tags as rule parameters

text = Text('Suured kollased kõrvad ja').tag_analysis()
rules =[
            ('A', 'blue'),
            ('S', 'green')
        ]
pp = PrettyPrinter(background='words', background_value=rules)
html = pp.render(text, True)

This time the defining parameters are 'A' and 'S' which stand for different word types. 'A' stands for 'Adjective' and
'S' stands for '...'. PrettyPrinter will sort everything else out by itself. The result of this will be:

<embed>
<!DOCTYPE html>

<html>
OK
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>


        mark.background_0 {
            background-color: blue;
        }
        mark.background_1 {
            background-color: green;
        }

    </style>
    <body>

        <mark class="background_0">Suured</mark> <mark class="background_0">kollased</mark> <mark class="background_1">kõrvad</mark> ja
    </body>
</html>
</embed>

As we can see from the results, all adjectives have been marked with a css background mark tag for color blue and the
noun in the sentence has been marked with a css background mark tag for color green. In this way it is possible to
visually separate all words that are of a specific type simply and effectively.

Example #4 Using different category visual representation dor different parts of text

text = Text('Esimene ja teine märgend')
        text.tag_with_regex('A', 'Esimene ja')
        text.tag_with_regex('B', 'ja teine')

        pp = PrettyPrinter(color='A', background='B')
        html = pp.render(text, False)

This time we want to highlight two different word types with different properties, font color and background color. To
do this, we have to both layers as PrettyPrinter class parameters and tie those to a certain value. With
text.tag_with_regex('A', 'Esimene ja') we bind the formating option in PerttyPrinter parameters 'color='A'' applies to
'Esimene ja' part of the text. What happens is that we will have two different css formats, each changing different
things. Here we can also see that the formatting works with overlapping layers, because the word 'ja' is in both 'A' and
'B'. The output with 'False' as the second parameter in render, will be the following:

<mark class="color">Esimene </mark><mark class="background color">ja</mark><mark class="background"> teine</mark> märgend

Here we can see, that the word 'ja' has two class tags, 'background' and 'color'.

Example #5
... content ...

