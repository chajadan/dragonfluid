.. include:: global.rst

Concepts
========


Overview
--------

Dragonfluid is focused on one task -- recognizing the occurrence of commands
in the middle of a dictation to allow multiple commands to be spoken in a row
without pauses.

When a rule is meant to allow passing off to other rules, it looks for
registered commands embedded in the dictation, and when it encounters one, the
whole utterance from that first command on is put aside. Once the rule finishes
processing, usually having put the dictation part of the utterance to use, the
put aside command portion is then mimic_'ed. To the speech recognition system,
the mimic_ seems like you just spoke the command right then. And since what was
mimic_'ed might contain several embedded commands, each rule simply cuts off
the part meant for it, and forwards the rest.


.. _registration:

Registration
------------

Registration is the recording of rules that are to be noticed when occurring in
the middle of an utterance. A registry holds this information and is consulted
when checking to see if an utterance has embedded commands.

One such registry is the `GlobalRegistry`, which is a type of dragonfly_
Grammar_. It can be used across files and the rules will all see each other.
It's a good default choice. If you have a need to isolate some rules, you can
use a `RegistryGrammar` to hold those rules. A `RegistryGrammar` can be local
to a single file, or potentially used across a subset of files, but it has no
awareness of the `GlobalRegistry`.


.. _intros:

Intros
......

When a rule is registered, what is actually registered is the initial fixed
literal text of the command spec, referred to as the **intros**. This process
is generally automatic, but can be guided. If a spec has only words and no
special elements, such as::

    spec = "next page"
    # intros = ["next page"]
    
then the entire command counts as the intro. If a command has any extra
elements in its spec, the intros stop at the first extra they encounter. For
instance::

    spec = "go to page <page_number>"
    # intros = ["go to page"] 
    
This means that any commands that begin with an extra will have an empty string
as their intro, and therefore will not be chained to from other commands.

If you noticed, intros is plural, because there can be many::

    spec = "(close|quit)"
    # intros = ["close", "quit"]
    
And it can get more complex::

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
result in less need for literal tags::

    intros = ["copy left word", "copy right word"]

Rules that undergo registration allow you to supply the intros directly to
override the automatically generated ones, either to the __init__ or as a class
attribute, similar to the spec.

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
mimic_'ed, match nothing, and depending on your setup, lose the whole rest of
the utterance which must then be repeated.
