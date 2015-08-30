.. suppress warning that this page is not in any doctree
 
:orphan:

.. _suitability:

The Impact Of Fluidity
======================

In general, commands have a special place in speech recognition systems. The
system puts extra effort into listening for them, giving them the benefit of
recognition in many cases. Imagine a phone system that only wants to hear
numbers from you -- it will try its hardest to map anything you say to one of
the number words it expects. "Sticks hate fun" could easily be accepted as 681.
Meanwhile free dictation has a specific bias to
hear common phrases and grammatical sentences. If you say "national wonderment",
the system may still recognize "national monument" even if it may have
considered wonderment a closer fit. And yes, if the fit was strong enough or
the surrounding context weak enough to override the "natural language bias",
then often it will render something less likely, such as "national wonderment".

When commands are spoken in a row for dragonfluid, only the first part of the
utterance will get the magical command seeking boost. Everything chained
afterward is subject to being recognized as free dictation. So it is not
surprising if you find that commands in the middle of utterances are not
recognized even if they never fail to be recognized when at the beginning of
utterances, especially if the commands consist of made up words or novel sounds.
This means that commands that up to now have always worked for you might present
challenges.

You can add novel command words to your vocabulary and attempt to train them
to be heard better, or you can alter your commands to things much more easily
recognized by your system. In the worst case, a pause between commands
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