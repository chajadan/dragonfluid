.. include:: global.rst

Welcome to dragonfluid!
=======================

About
-----

The dragonfluid library is a simple extension to `dragonfly`_, a library to
create :term:`rules or macros <rule>` that work with Dragon NaturallySpeaking
or Windows Speech Recognition. dragonfluid adds "out of the box"
support for :term:`chaining` multiple commands in a row without pausing during
speech. You are assumed to be familiar with dragonfly_ and its use.


It's Not For Everyone
---------------------

If you have existing :term:`voice commands <voice command>` whose words you
absolutely do not want to
alter, dragonfluid might not be for you, especially if those commands consist of
hoots, made up words, or novel syllables. If you are willing to alter your
commands then little should get in your way. I recommend trying in any case
rather than assuming the worst if you're interested in easy to add on chaining
support, but thought you should know in advance it's not equally great with all
scenarios.

You may want to read further details regarding `The Effect Of Fluidity
<suitability>` on command recognition, especially if you have strange commands
or commands you cannot or will not alter.


Quick Start
-----------

The easiest way to give it a whirl is to:

- use ``pip install dragonfluid`` to install dragonfluid,
- import the following objects into your code,

::

    from dragonfluid import GlobalRegistry, FluidRule, QuickFluidRules

- replace any `Grammar <dragonfly.grammar.grammar_base.Grammar>` class with
  `GlobalRegistry`,
- replace any `CompoundRule <dragonfly.grammar.rule_compound.CompoundRule>`
  class with `FluidRule`,
- replace any `MappingRule <dragonfly.grammar.rule_mapping.MappingRule>` class
  with `QuickFluidRules`,
- reload your macro files!

You don't have to change all your files at once, but :term:`chaining` will
generally occur only between dragonfluid rule types added to dragonfluid
grammars.


How To Speak
------------

Just speak naturally. Don't worry if pauses are needed, speak as if you
trust they are not, and only then address the situations where the intended
functionality does not result.

However, now that you can speak multiple commands in a row,
there is an additional need to say a literal tag before anything that looks
like a command but is not meant to be one. The default :term:`literal tag`
options are "literal", "english", and "English". For additional details
see the `literalization concept section <literalization>`.
