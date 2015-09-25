from collections import Counter

from dragonfly import Grammar

from dragonfluid._specparsers import _XmlSpecParser
from dragonfluid._support import _first_not_none, _safe_kwargs

class Registry(object):
    """
    A registry maintains information about a set of known active rules and the
    `literal tags <literalization>` that must precede their `intros <intros>`
    when their commands are meant as free speech dictation.
    
    Working directly with a Registry object is an advanced use case.
    
    A registry exposes services regarding inspection and parsing of utterances
    as it relates to its literal tags and currently actively registered
    commands.
    """
    
    literal_tags = ["English", "english", "literal"]
    """
    `Literal tags <literalization>` are used during speech to indicate that what
    follows is not a command. Registry object's initialize with these default values.
    """
    
    def __init__(self, literal_tags=[], override_tags=False):
        """
        :param literal_tags: These words will function as `literalization
            <literalization>` markers to indicate that what
            follows is not a command, but rather free speech dictation.
        :type literal_tags: string list
        :param bool override_tags: If False, the literal_tags supplied to
            __init__ will be added to the defaults, otherwise they will
            replace them.
        """
        self.literal_tags = literal_tags
        if not override_tags:
            self.literal_tags += Registry.literal_tags
        self._registered_commands = Counter()
        self._command_partials = Counter()
            
    def translate_literals(self, words_iterable):
        """
        Returns a list of words, stripped of :term:`literal tags <literal tag>`
        in a semantically meaningful way. Final isolated literal_tag's are
        stripped.

        When a literal_tag precedes a literal_tag, the second occurrence only
        is retained.
        
        In a string of all literal_tag's, exactly the odd indexed ones
        (in a 0-indexed sense) would be returned.
        """
        translation = []
        words_iterator = iter(words_iterable)

        for word in words_iterator:
            if word in self.literal_tags:
                try:
                    word = words_iterator.next()
                    translation.append(word)
                except StopIteration:
                    break
            else:
                translation.append(word)
        
        return translation

    def _get_literal_tag_indices(self, words_iterable):
        """
        Returns a list of indices where literal tags occur for the purpose of
        being literal tags.
        """
        indices = []
        words_iterator = enumerate(words_iterable)

        for i, word in words_iterator:
            if word in self.literal_tags:
                indices.append(i)
                words_iterator.next() # skip the next i, word pair
        
        return indices
    
    def register_rule(self, rule):
        """
        Adds the rule to a list of known active rules. Not generally called
        directly by users. For more information see
        the `registration <registration>` concept section.
        """
        intros = self._get_intros(rule)
        partials = self._get_partials(rule, intros)
        self._registered_commands.update(intros)
        self._command_partials.update(partials) 
 
    def unregister_rule(self, rule):
        """
        Removes the rule from the list of known active rules. Not generally
        called directly by users.
        """
        intros = self._get_intros(rule)
        partials = self._get_partials(rule, intros)
        self._registered_commands.subtract(intros)
        self._command_partials.subtract(partials)
    
    def is_registered(self, intro):
        """
        :param string command_intro: A command :term:`intro` to test for
            `registration <registration>`.
        :returns: True if registered, False otherwise
        :rtype: bool
        """ 
        return self._registered_commands[intro] > 0
    
    def has_partial(self, partial_command):
        """
        Returns True if the string supplied is an initial substring of a
        registered intro, assuming only full words are supplied.
        """
        return self._command_partials[partial_command] > 0

    def starts_with_registered(self, words_iterable):
        """
        Returns True if the iterable of strings begins with the words of a
        registered command.
        """
        running_match = ""
        words_iterator = iter(words_iterable)
        for word in words_iterator:
            if word in self.literal_tags:
                words_iterator.next()
                continue
            
            if running_match:
                running_match += " "
            running_match += word
            if self.is_registered(running_match):
                return True
            elif not self.has_partial(running_match):
                return False
    
    def _determine_command_index(self, dictation_words):
        if not dictation_words:
            return None
        
        word_count = len(dictation_words)
        start_index = 0
        while start_index < word_count:
            if dictation_words[start_index] in self.literal_tags:
                start_index += 2
                continue
            words_iterable = (dictation_words[i] for i in xrange(start_index, word_count))
            if self.starts_with_registered(words_iterable):
                return start_index
            start_index += 1
        return word_count
    
    def _split_dictation(self, dictation):
        return self._split_dictation_words_list(dictation.words)

    def _split_dictation_words_list(self, dictation_words_list):
        if not dictation_words_list:
            return None, None
        command_index = self._determine_command_index(dictation_words_list)
        if command_index is None: # indicates an error
            return None, None
        return dictation_words_list[:command_index], dictation_words_list[command_index:]
    
    @staticmethod
    def _determine_intros(rule):
        """
        Expected to be able to accept any spec as long as it is well-formed:
        - balanced parentheses and brackets
        - contains no { or } characters
        - outside of <extra> references, contains no < or > characters
        
        This could be further enhanced to extract string parts from Option elements
        e.g.    spec = "select <direction> word"
                extras = (Choice("direction", {"left":"left", "right":"right"}), )
                ### intros --> ["select right word", "select left word"]
        """
        if rule._intros:
            return rule._intros
        else:
            intros_spec = _first_not_none(getattr(rule, "_intros_spec", None), getattr(rule, "_spec", None))
            if not intros_spec:
                return None
            return Registry._parse_spec(intros_spec)
    
    @staticmethod
    def _determine_partials(rule, intros=None):
        partials = []
        intros = _first_not_none(intros, Registry._get_intros(rule))
        for intro in intros:
            position = intro.rfind(" ")
            while position != -1: # -1 means down to final word, not a partial
                partials.append(intro[0:position])
                position = intro.rfind(" ", 0, position)
        return partials
    
    @staticmethod
    def _get_intros(rule):
        if getattr(rule, "_is_registered", False):
            if not rule._determined_intros:
                rule._determined_intros = Registry._determine_intros(rule)
            return rule._determined_intros               
        else:
            return []

    @staticmethod
    def _get_partials(rule, intros=None):
        if getattr(rule, "_is_registered", False):
            if not rule._determined_partials:
                rule._determined_partials = Registry._determine_partials(rule, intros)
            return rule._determined_partials
        else:
            return []
    
    @staticmethod
    def _parse_spec(spec):
        try:
            parser = _XmlSpecParser(spec)
            return parser.get_intros()
        except:
            print "Registry could not parse this spec for intros:", spec
            return None


class RegistryGrammar(Grammar):
    """
    A RegistryGrammar is like a normal Grammar_ object, except it registers
    and unregisters `RegisteredRule`'s as they are activated and deactivated,
    maintaining a registry of those that are currently active.
    
    `ContinuingRule`'s that are added to this grammar will automatically use
    this object's registry when seeking out commands embedded in utterances.
    """
    
    def __init__(self, name, registry=None, **kwargs):
        """
        :param name: Passed to dragonfly Grammar_
        :param Registry registry: The Registry object that serves as the
            active `registration` list. It may be shared across
            RegistryGrammar instances. If None, a local Registry object is
            created.
        :param \*\*kwargs: Passed safely to dragonfly Grammar_
        """
        self.registry = _first_not_none(registry, Registry())
        _safe_kwargs(Grammar.__init__, self, name, **kwargs)

    # override -- you're not expected to need to know this is in place
    def activate_rule(self, rule):
        if getattr(rule, "_is_registered", False):
            self.registry.register_rule(rule)
        Grammar.activate_rule(self, rule)
     
    # override -- you're not expected to need to know this is in place
    def deactivate_rule(self, rule):
        if getattr(rule, "_is_registered", False):
            self.registry.unregister_rule(rule)
        Grammar.deactivate_rule(self, rule)
     
    # override -- you're not expected to need to know this is in place
    def unload(self):
        for rule in self._rules:
            # unregister to prevent multiply registered rules during restart
            rule.deactivate()
        Grammar.unload(self)


class GlobalRegistry(RegistryGrammar):
    """
    The GlobalRegistry is a `RegistryGrammar` with a single globally shared
    `Registry`. It can be used as the Grammar_ object across many files,
    allowing the rules to know about each other for chaining.
    """
    
    registry = Registry()
    
    def __init__(self, name, description=None, context=None, engine=None, **kwargs):
        """
        :param name: Passed to dragonfly Grammar_
        :param description: Passed to dragonfly Grammar_
        :param context: Passed to dragonfly Grammar_
        :param engine: Passed to dragonfly Grammar_
        :param \*\*kwargs: Passed to `RegistryGrammar`
        """
        kwargs["description"] = description
        kwargs["context"] = context
        kwargs["engine"] = engine
        RegistryGrammar.__init__(self, name, self.registry, **kwargs)
