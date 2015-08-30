.. include:: global.rst

Concepts
========


Overview
--------

dragonfluid is primarily focused on one task -- recognizing the occurrence of
commands in the middle an :term:`utterance` to allow multiple commands to be
spoken in a row without pauses.

When a :term:`rule` is meant to allow :term:`chaining` to other rules, it looks
for
:term:`registered commands <registered command>` embedded in the utterance that
triggered it, and when it encounters one, the
whole utterance from that first command on is put aside. Once the rule finishes
processing, the
put aside command portion is then mimic_'ed. To the speech recognition system,
the mimic_ seems like you just spoke the command right then. And since what was
mimic_'ed might contain several chained commands, each rule simply cuts off
the part meant for it, and forwards the rest.


.. _registration:

Registration
------------

Registration is the recording of :term:`commands <command>` that are to be
noticed from within the middle of an :term:`utterance`. A `Registry` holds this
information and is consulted by rules that perform :term:`chaining` when
checking to see if an utterance has :term:`embedded commands <embedded
commands>`.

The most common use of a `Registry` is through the `GlobalRegistry`, which is a
type of dragonfly_ `Grammar <dragonfly.grammar.grammar_base.Grammar>`. It can be
used across files and the rules will all see each other.
It's a good default choice. If you have a need to isolate some rules, you can
use a `RegistryGrammar` to hold those rules. A `RegistryGrammar` or the `Registry`
it holds can be used locally within a single file, or potentially used across a
subset of files, but it has no awareness of what is registered in the
`GlobalRegistry`.


.. _intros:

Intros
------

When a rule is `registered <registration>`, the initial fixed
literal text of the command spec is determined and remembered to act as a
trigger that the command occurred. These triggers are referred to as the
:dfn:`intros`. This process is largely automatic, but can be guided.

If a :term:`spec` has only words and no :term:`extras <extra>` elements, such
as::

    spec = "next page"
    # intros = ["next page"]
    
then the entire spec counts as the intro. If a spec has any extra
elements in it, the intros stop at the first extra they encounter. For
instance::

    spec = "go to page <page_number>"
    # intros = ["go to page"] 
    
This means that any commands whose spec begins with an extra will have an empty
string as its intro, and therefore will not be :term:`chained <chaining>` to
from other commands.

Intros is plural, because there can be many::

    spec = "(close|quit)"
    # intros = ["close", "quit"]
    
And it can get arbitrarily complex::

    spec = "(go [to]|at) next line"
    # intros = ["go next line", "go to next line", "at next line"]
    
Each intro will be as long as possible until an extra is encountered::

    spec = "(insert <part>|delete) below this line"
    # intros = ["insert", "delete below this line"]

Lastly, consider the following scenario::

    spec = "copy <direction> word"
    extras = (Choice("direction", {"left":"left", "right":"right"}), )
    # intros = ["copy"]
    
The automatic generation of intros stops at the ``direction`` extra, but we can
tell that all cases can be determined in advance. The following intros would
result in less need for :term:`literal tags <literal tag>`::

    intros = ["copy left word", "copy right word"]

Rules that undergo registration allow you to supply the intros directly to
override the automatically generated ones, supplied either to the __init__ or as
a class attribute, similar to the spec. So we could supply these improved upon
intros.
There is a short cut option called **intro_spec** that, instead of supplying
individual intros, lets you give a new spec from which to derive them. Our
original scenario would then look like::

    spec = "copy <direction> word"
    intros_spec = "copy (left|right) word"
    extras = (Choice("direction", {"left":"left", "right":"right"}), )
    # intros = ["copy left word", "copy right word"]

When supplying intros, directly or through intros_spec, you must supply
appropriate values, for if you have no "zixo" command but you place that in a
list of intros, if "zixo" occurs in the middle of an utterance, it will get
mimic_'ed along with all that follows, the mimic will match no commands, and
depending on your setup, that whole rest of the :term:`utterance` will be lost
and must then be repeated.


.. _literalization:

Literalization
--------------

Literalization in the context of dragonfluid is an indication that something
said, even though it may look like a `registered <registration>` command, is
actually intended as :term:`free speech dictation`. This is accomplished by
preceded these command impostors with a spoken
:dfn:`literal tag`. The default options are "literal", "english", and "English",
and they are configurable. It is `Registry`'s that maintain and work with
literal tags.

You don't necessarily need to literalize every word that begins a command. If
you have a command "drop previous element <words>" in your arsenal but no other
commands begin with the word drop, then you would not need to literalize the
word drop unless it was followed by the words "previous element". So "drop me a
line" could be said plainly. Commands are recognized only by any one of their
`registered <registration>` :term:`intros <intro>`, avoiding any need for
literalization when possible.

You can further minimize the need for literal tags by crafting your commands to
not sound like things you tend to dictate. Simple strategies include using rarer
words or making commands sound more like headlines or Tarzan speak.

If you actually want to use a literal tag in free speech, just precede it by any
literal tag, including itself. "English English" and "literal English" both just
`translate <translation>` to "English".

When a literal tag has been literalized to serve as :term:`free speech
dictation`, it does not serve as a literal tag for what follows.


.. _translation:

Translation
-----------

Translation in the context of dragonfluid is taking exact words spoken by
the user that may or may not contain :term:`literal tags <literal tag>`, and
producing the intended free speech that results from removing any literal tags
whenever they are serving the role of literal tags. This is the most common
desired form when grabbing free speech dictation for use in the processing of
your rules, such as when outputting text to an entry field or document.

Translation happens behind the scenes in the Dictation_ elements of
`FluidRule`'s. More advanced usage requires a choice of translated versus
non-traslated results, and `SplitDictation` objects can return either.