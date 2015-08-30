.. include:: global.rst

Glossary
========

.. glossary::

	chaining
		The ability to invoke multiple recognition elements in a row by speaking
		them as a single :term:`utterance`, i.e. without pausing between them.
		In dragonfluid, chains may be of any length.
		Depending on the scenario, two neighboring chained elements may be
		comprised of free speech dictation and a command, in either order, or a
		pair of commands.
		
		Only rules derived from `ContinuingRule` will pass off, or chain, to
		successive commands. 
	
	command action
		The action executed when a :term:`rule` is triggered by its
		:term:`command`. 
		 
	command
		Spoken content within an :term:`utterance` that is meant to trigger the
		execution of a :term:`command action`. Often specified in the form of a
		:term:`spec`. In contrast with :term:`dictation`.
		
	dictation
	free speech dictation
		Spoken content within an :term:`utterance` that is meant to be captured
		as its textual representation, generally as a means to supply content to
		a :term:`command action`, such as for printing to the screen. In
		contrast with a :term:`command`.
	
	dictation container
		A type of value produced by a `Dictation
		<dragonfly.grammar.elements_basic.Dictation>` element, derived from
		`DictationContainerBase
		<dragonfly.engines.base.dictation.DictationContainerBase>`, and specific
		to the speech recognition system in use. The elements provided by
		dragonfluid, such a `SplitDictation` can also return these containers
		upon request.
	
	embedded command
		A :term:`command` within an :term:`utterance` that does not occur at the
		beginning of the utterance.
	
	extras
		Broadly speaking, an extra is a part of a command that hears and results
		in a certain type of content.
		
		An extra uses a named element, derived from
		`ElementBase <dragonfly.grammar.elements_basic.ElementBase>`,
		and provides a value, such as text or a :term:`dictation container`.
		Dragonfly documentation provides :ref:`a list of elements
		<refelementclasses>`.
		
		It is often used here as a term for the dictionary of extras passed
		to the _process_recognition callback of a rule. You are generally
		expected to know how to access the various extras from this dictionary,
		and when documentation states that extras are passed to or returned from
		a function, the form implied is this dictionary. Note that this
		dictionary generally does not container the underlying element that
		generates a value, so extras are distinct from elements, with extras
		using elements and producing values under the same name.
		
	intro
	command intro
		The initial part of a command's :term:`spec`, consisting only of static
		literal words, up to the first encountered :term:`extra <extras>`
		reference in angle brackets. For further details see the `intros
		<intros>` concept section.
		
	literal tag
		A word spoken within an :term:`utterance` to specific that what follows
		is :term:`free speech dictation` even when it looks a :term:`command`
		or literal tag. For further details see the `literalization
		<literalization>` concept section. 

	registered command
		A command that can be triggered from within the middle of an
		:term:`utterance`. For further details see the `registration
		<registration>` concept section. 
		
		
	rule
	macro
		A triggerable event. The trigger is the :term:`command` and the event
		triggered is the :term:`command action`.
		
	spec
		A common dragonfly_ attribute that determines which spoken
		words will trigger a :term:`rule`. It may be a fixed literal command
		spec, such as "show desktop", or it may include references to
		:term:`extras` in angle brackets, such as "delete left <characterCount>
		characters".
		
	utterance
		The contiguous stream of spoken content captured by your speech
		recognition system starting from the moment your it determines you have
		begun speaking through until the moment it encounters enough silence to
		qualify as a pause given its configuration.