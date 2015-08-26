from collections import Counter

from dragonfly import Grammar

from dragonfluid._specparsers import _XmlSpecParser
from dragonfluid._support import _first_not_none, _safe_kwargs

class _Registry(object):
    
    literal_tags = ["English", "english", "literal"]
    """
    Literal tags are used during speech to indicate that what follows is not a
    command. _Registry object's initialize with these default values.
    """
    
    def __init__(self):
        self.literal_tags = _Registry.literal_tags
        self._registered_commands = Counter()
        self._command_partials = Counter()


    @staticmethod               
    def translate_literals(words_iterable):
        """
        Returns a list of words, stripped of literalizer tags in a semantically
        meaningful way. Final isolated literal_tag's are stripped.
        """
        
        """
        When a literal_tag precedes a literal_tag, the second occurrence only
        is retained.
        
        In a string of all literal_tag's, exactly the odd indexed ones
        (in a 0-indexed sense) would be returned.
        """
        translation = []
        words_iterator = iter(words_iterable)

        for word in words_iterator:
            if word in _Registry.literal_tags:
                continue
            translation.append(word)
        
        return translation
    
    @staticmethod               
    def _get_literal_tag_indices(words_iterable):
        """
        Returns a list of indices where literal tags occur for the purpose of
        being literal tags.
        """
        indices = []
        words_iterator = enumerate(words_iterable)

        for i, word in words_iterator:
            if word in _Registry.literal_tags:
                indices.append(i)
                words_iterator.next() # skip the next i, word pair
        
        return indices
    
    def register_rule(self, rule):
        intros = self._get_intros(rule)
        partials = self._get_partials(rule, intros)
        self._registered_commands.update(intros)
        self._command_partials.update(partials) 
 
    def unregister_rule(self, rule):
        intros = self._get_intros(rule)
        partials = self._get_partials(rule, intros)
        self._registered_commands.subtract(intros)
        self._command_partials.subtract(partials)
    
    def is_registered(self, command):
        return self._registered_commands[command] > 0
    
    def has_partial(self, partial_command):
        return self._command_partials[partial_command] > 0

    def starts_with_registered(self, words_iterable):
        running_match = ""
        words_iterator = iter(words_iterable)
        for word in words_iterator:
            if word in self.literal_tags:
                words_iterator.next()
                continue
            
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
            return _Registry._parse_spec(intros_spec)
    
    @staticmethod
    def _determine_partials(rule, intros=None):
        partials = []
        intros = _first_not_none(intros, _Registry._get_intros(rule))
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
                rule._determined_intros = _Registry._determine_intros(rule)
            return rule._determined_intros               
        else:
            return []

    @staticmethod
    def _get_partials(rule, intros=None):
        if getattr(rule, "_is_registered", False):
            if not rule._determined_partials:
                rule._determined_partials = _Registry._determine_partials(rule, intros)
            return rule._determined_partials
        else:
            return []
    
    @staticmethod
    def _parse_spec(spec):
        try:
            parser = _XmlSpecParser(spec)
            return parser.get_intros()
        except:
            print "_Registry could not parse this spec for intros:", spec
            return None


class RegistryGrammar(Grammar):
    
    def __init__(self, name, registry=None, **kwargs):
        """
        kwargs safely passed to drafonly Grammar, to allow for future
        supported parameters.
        """
        self._registry = _first_not_none(registry, _Registry())
        _safe_kwargs(Grammar.__init__, self, name, **kwargs)

    # override -- you're not expected to need to know this is in place
    def activate_rule(self, rule):
        if getattr(rule, "_is_registered", False):
            self._registry.register_rule(rule)
        Grammar.activate_rule(self, rule)
     
    # override -- you're not expected to need to know this is in place
    def deactivate_rule(self, rule):
        if getattr(rule, "_is_registered", False):
            self._registry.unregister_rule(rule)
        Grammar.deactivate_rule(self, rule)
     
    # override -- you're not expected to need to know this is in place
    def unload(self):
        for rule in self._rules:
            # unregister to prevent multiply registered rules during restart
            rule.deactivate()
        Grammar.unload(self)


class GlobalRegistry(RegistryGrammar):
    _registry = _Registry()
    
    def __init__(self, name, description=None, context=None, engine=None, **kwargs):
        """kwargs passed to RegistryGrammar"""
        RegistryGrammar.__init__(self, name, self._registry, **kwargs)
