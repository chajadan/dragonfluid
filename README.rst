dragonfluid
===========

About
-----

The dragonfluid library is a simple extension to `dragonfly`_, a library to
create voice commands  or 'macros' that work with Dragon NaturallySpeaking or
Windows Speech Recognition. dragonfluid adds "out of the box"
support for speaking multiple commands in a row without pausing.

It's Not For Everyone
---------------------

If you have existing voice commands whose words you absolutely do not want to
alter, dragonfluid might not be for you unless you are lucky enough
that your speech recognition system is either easily trained (something we all
recognize is not a given), or your command words are natural enough English
that your system is willing to hear them in the context of a sentence. Strange
hoots, made up words, and novel syllables are not something easily recognized
in a dictation, even when as commands they are picked up quite readily.

In general, commands have a special place in speech recognition systems. The
system puts extra effort into listening for them, giving them the benefit of
recognition in many cases. Imagine a phone system that only wants to hear
numbers from you -- it will try its hardest to map anything you say to one of
the number words it expects. Meanwhile free dictation has a specific bias to
hear common phrases and grammatical sentences. If you say "national wonderment",
the system may still recognize "national monument" even if it may have
considered wonderment a closer fit. And yes, if the fit was strong enough or
the surround context weak enough to override the "natural language bias", then
often it will render something less likely, such as "national wonderment".

When commands are spoken in a row for dragonfluid, only the first part of the
utterance will get the magical command seeking boost. Everything chained
afterward is subject to being recognized as free dictation. So it is not
surprising if you find that commands in the middle of utterances are not
recognized even if they never failed to be recognized when used by you only as
commands, especially if they are made up words or novel sounds.

You can add novel command words to your vocabulary and attempt to train them
to be heard better, or you can alter your commands to things much more easily
recognized by your system. In the worst case, a pause between before commands
stills works, but that's not very dragonfluid is it.

Case-sensitivity can come into the picture as well. A command of "english" will
not be triggered if possible vocabulary values or formatting turns the word into
"English", but start off a sentence with the word "English" and suddenly the
magical boost of commands will just ignore the capital letter in it's attempt to
match something from the commands it expects.

In general, if you can dictate your list of commands easily into a plain text
document, you should be good to go. If you're willing to alter your commands
then nothing should be able to get in your way! And if you're really dead set
on some crazy alien sounding system you devised and loved, then it's all up
to how trainable your speech recognition system is in the context of free
dictation.


Quick Start
-----------

The easiest way to give it a whirl is:

::

    from dragonfluid import GlobalRegistry, FluidRule, QuickFluidRules

Then,

- replace any dragonfly Grammar_ class with `GlobalRegistry`,
- replace any dragonfly CompoundRule_ with `FluidRule`,
- replace any dragonfly MappingRule_ with `QuickFluidRules`,
- reload your macros!

You don't have to change all your files at once, but chaining will occur only
between fluid rule types added to the GlobalRegistry.


How To Speak
------------

Just speak naturally. Don't worry if pauses are needed, speak as if you
trust they're not. However, now that you can speak multiple commands in a row,
there is an additional need to say a "literal tag" before anything that looks
like a command but is not meant to be one. The default literal tag options are
"literal", "english", and "English".

You don't necessarily need to literalize every word that begins a command. If
you have a command "drop previous element <words>" in your arsenal but no other
commands begin with the word drop, then you would not need to literalize the
drop in "drop me a line", or any instance of "drop" not following by "previous
element". "drop previous element" is the "command intro", and these intros are
automatically determined from the spec of commands, consisting of all literal
words up to the first extra reference in angle brackets. Though in some cases,
you may have to literalize a couple words in a row.

You can minimize the need for literal tags by crafting your commands to not
sound like things you tend to dictate, more like headlines than normal
sentences, or with words you're not likely to use in free dictation.

If you actually want to use a literal tag in free speech, just saw it twice, as
in "English English", or precede it with any other literal tag you wish, as in
"literal English", where "literal" would serve the purpose of a literal tag so
that "English" would come across as an intended dictation.


Learn More
-------------------

Coming soon: ReadTheDocs_

.. _ReadTheDocs: http://dragonfluid.readthedocs.org/en/latest/
.. _dragonfly: http://dragonfly.readthedocs.org/en/latest/
.. _Grammar: http://dragonfly.readthedocs.org/en/latest/grammar.html#dragonfly.grammar.grammar_base.Grammar
.. _CompoundRule: http://dragonfly.readthedocs.org/en/latest/rules.html#compoundrule-class
.. _MappingRule: http://dragonfly.readthedocs.org/en/latest/rules.html#mappingrule-class