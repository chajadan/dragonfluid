from dragonfly import Dictation

from dragonfluid._grammars import GlobalRegistry
from dragonfluid._support import _safe_kwargs


class _RegistryElement(object):
    # An internal object used to indicate that the element has a _registry
    # attribute due to its use of Registry services
    pass

class SplitDictation(_RegistryElement, Dictation):
    """
    A rule element used to split recognized dictation into an initial free
    dictation part, and a following command part. Either part is optional,
    unless the element is initialized with the forced_dictation element to True.
    
    The following example shows this element being used and retrieved in the
    standard expected way.
    
    ::
    
        from dragonfluid import RegistryRule, SplitDictation
        
        class SplitterRule(RegistryRule):
            spec = "set name <name_split>"
            extras = (SplitDictation("name_split"), )
            def _process_recognition(self, node, extras):
                name_split = extras["name_split"]
                name = name_split.dictation
                
    The result is a type of container from which parts of the result may be
    retrieved. The full list of attributes are individually documented below,
    but a simple naming scheme is in place. The first part of the attribute
    name indicates the part desired:
    
    * **full** - The entire utterance
    * **dictation** - The utterance only up to the first accepted command, may
      be the empty string if the utterance began with an accepted command
    * **command** - The rest of the utterance starting with the first accepted
      command, through the end of the utterance
      
    The second part indicates the return type desired:
    
    * **_words** - A string list of the words
    * **_container** - The same type of dictation container that a Dictation
      element would yield, some derived class of BaseDictationContainer
      as appropriate for the speech recognition system in use.
    * *default* - If neither of the above are indicated, the default result type
      is a string.
      
    The third part indicates whether literal tags should be retained or
    translated out:
    
    * **_notrans** - Retain the literal tags
    * **_trans** - Strip literal tags and return only the intended content
    * *default* - If neither of the above are indicated, the result will have
      the default behavior most common when using the part requested. **full** and
      **command** parts will retain literal tags, while **dictation** parts will
      strip them so as to only return the intended free speech. Default
      translation of the parts applies to all return types.
      
    There is also an issue of formatting. The various dictation containers
    have a formatting option. For Windows Speech Recognition there is no real
    formatting provided beyond separating words with spaces. Dragon
    NaturallySpeaking provides more sophisticated formatting. All return types
    except for the **_container** values have formatting applied to the result
    returned. If you absolutely do not want the formatting applied, you must
    request the containers directly, from which you can choose to apply
    formatting or not. If you choose a **_trans** container, it will have had
    literal tags stripped, but otherwise be unmodified.
    
    """
    def __init__(self, name, registry=None,
                 forced_dictation=False, **kwargs):
        """

        :param string name: The name of this element, used as the keyname in the
            extras dictionary passed back to _process_recognition
        :param `Registry` registry: The `Registry` instance that determines what
            words form a command and what literal tags are in effect. If None,
            the `ActiveGrammarRule` decorator will set the registry of any
            `RegistryGrammar` derived instance the containing rule is added to.
        :param bool forced_dictation: When True, refuses to recognize
            utterance-initial commands, so as to ensure this element returns
            non-empty free dictation.
        :param kwargs: Passed safely to Dictation.__init__
        
        """
        self._registry = registry
        self._forced_dictation = forced_dictation
        _safe_kwargs(Dictation.__init__, self, name=name, **kwargs)
    
    @property
    def registry(self):
        if self._registry:
            return self._registry
        else:
            return GlobalRegistry.registry
    
    @registry.setter
    def registry(self, value):
        self._registry = value
    
    def value(self, node):
        # The element instance lives on between invocations of the rule in
        # which it lives. This value method is called from each invocation to
        # obtain the *current* value. Therefore below we reset any state so
        # that elements retrieved respect the `node` passed in.
        
        self._node = node # store the context node from which to parse values
        # clear memoize variables of any previous values
        self._formatted_words_list_memo = None
        self._command_index_memo = None
        return self
    
    @property
    def command_index(self):
        """
        Returns the 0-based word index at which the first accepted full command
        intro occurs, or the index beyond last if no such intro occurs. If
        forced_dictation was set True during initialization, any
        utterance-initial command will be skipped to ensure dictation content
        is non-empty.
        """
        if self._command_index_memo is None:        
            command_index = self.registry._determine_command_index(self._formatted_words_list)
            if self._forced_dictation and command_index == 0:
                # do not allow empty dictation bypass utterance-initial command
                next_command_index = self.registry._determine_command_index(self._formatted_words_list[1:])
                if next_command_index is not None:
                    command_index = next_command_index + 1
                else:
                    # return index beyond last as None indicator
                    command_index = len(self._formatted_words_list)
            self._command_index_memo = command_index             
        return self._command_index_memo
    
    def translate(self, words_iterable):
        """Returns a word list, as translated."""
        return self.registry.translate_literals(words_iterable)    
    
    def mimic_command(self):
        command = self.command_words_notrans
        if command:
            self._node.engine.mimic(command)
        
    def mimic_full(self):
        full = self.full_words_notrans
        if full:
            self._node.engine.mimic(full)    
    
    @property
    def full(self):
        """Alias for `full_notrans`."""
        return self.full_notrans
    
    @property
    def full_notrans(self):
        """
        Returns the full content, as a string, with formatting applied and with
        literal tags retained.
        """        
        return " ".join(self.full_words_notrans)
    
    @property
    def full_trans(self):
        """
        Returns the full content, as a string, with formatting applied and with
        literal tags translated to their intended result.
        """
        return " ".join(self.full_words_trans)
    
    @property
    def full_words(self):
        """Alias for `full_words_notrans`."""
        return self.full_words_notrans
    
    @property
    def full_words_notrans(self):
        """
        Returns the full content, as a word list, with formatting applied and
        with literal tags retained.
        """        
        return self._formatted_words_list
    
    @property
    def full_words_trans(self):
        """
        Returns the full content, as a word list, with formatting applied and
        with literal tags translated to their intended result.
        """
        return self.translate(self.full_words_notrans)

    @property
    def full_container(self):
        """Alias for `full_container_notrans`.""" 
        return self.full_container_notrans
    
    @property
    def full_container_notrans(self):
        """
        Returns the full content, as a BaseDictationContainer of the
        appropriate type given the speech recognition system in use, without
        any alterations of any sort applied to the container contents. 
        """
        return self._node.engine.DictationContainer(self._node.words())
    
    @property
    def full_container_trans(self):
        """
        Returns the full content, as a BaseDictationContainer of the
        appropriate type given the speech recognition system in use, with no
        formatting applied yet with literal tags translated to their intended result. 
        """
        tag_indices = self.registry._get_literal_tag_indices(self.full_words_notrans)
        notrans_words = self._node.words()
        translated_words = [notrans_words[i] for i in range(len(notrans_words)) if i not in tag_indices]
        return self._node.engine.DictationContainer(translated_words)
    
    @property
    def dictation(self):
        """Alias for `dictation_trans`."""
        return self.dictation_trans
    
    @property
    def dictation_trans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a string with formatting and with literal tags
        translated to their intended result.
        """        
        return " ".join(self.dictation_words_trans)
    
    @property
    def dictation_notrans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a string with formatting and with literal tags
        retained.
        """
        return " ".join(self.dictation_words_notrans)
    
    @property
    def dictation_words(self):
        """Alias for `dictation_words_trans`."""    
        return self.dictation_words_trans
    
    @property
    def dictation_words_trans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a word list with formatting and with literal
        tags translated to their intended result.
        """        
        return self.translate(self.dictation_words_notrans)
    
    @property
    def dictation_words_notrans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a word list with formatting and with literal
        tags retained.
        """        
        return self._formatted_words_list[:self.command_index]
    
    @property
    def dictation_container(self):
        """Alias for `dictation_container_trans`."""
        return self.dictation_container_trans
    
    @property
    def dictation_container_notrans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a BaseDictationContainer of the appropriate type
        given the speech recognition system in use, without any alterations
        of any sort applied to the container contents. 
        """
        return self._node.engine.DictationContainer(self._node.words()[:self.command_index])    
    
    @property
    def dictation_container_trans(self):
        """
        Returns any and all content up to the first full command intro, if any.
        Content is returned as a BaseDictationContainer of the appropriate type
        given the speech recognition system in use, with no formatting applied
        yet with literal tags translated to their intended result.   
        """
        tag_indices = self.registry._get_literal_tag_indices(self.dictation_words_notrans)
        notrans_words = self._node.words()[:self.command_index]
        translated_words = [notrans_words[i] for i in range(len(notrans_words)) if i not in tag_indices]
        return self._node.engine.DictationContainer(translated_words)
    
    @property
    def command(self):
        """Alias for `command_notrans`"""
        return self.command_notrans
    
    @property
    def command_notrans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a string with formatting and with literal
        tags retained.
        """
        return " ".join(self.command_words)
    
    @property
    def command_trans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a string with formatting and with literal
        tags retained.
        """
        return " ".join(self.command_words_trans)    
    
    @property
    def command_words(self):
        """Alias for `command_words_notrans`"""
        return self.command_words_notrans

    @property
    def command_words_notrans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a word list with formatting and with
        literal tags retained.
        """
        return self._formatted_words_list[self.command_index:]
    
    @property
    def command_words_trans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a word list with formatting and with
        literal tags translated to their intended result.
        """
        return self.translate(self.command_words)    
    
    @property
    def command_container(self):
        """Alias for `command_container_notrans`"""
        return self.command_container_notrans

    @property
    def command_container_notrans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a BaseDictationContainer of the appropriate
        type given the speech recognition system in use, without any
        alterations of any sort applied to the container contents.
        """
        return self._node.engine.DictationContainer(self._node.words()[self.command_index:])
    
    @property
    def command_container_trans(self):
        """
        Returns any and all content starting from first full command intro, if
        any. Content is returned as a BaseDictationContainer of the appropriate
        type given the speech recognition system in use, with no formatting
        applied yet with literal tags translated to their intended result.  
        """
        tag_indices = self.registry._get_literal_tag_indices(self.command_words_notrans)
        notrans_words = self._node.words()[self.command_index:]
        translated_words = [notrans_words[i] for i in range(len(notrans_words)) if i not in tag_indices]
        return self._node.engine.DictationContainer(translated_words)    

    @property
    def _formatted_words_list(self):
        if getattr(self, "_formatted_words_list_memo", None) is None:
            self._formatted_words_list_memo = self._node.engine.DictationContainer(self._node.words()).format().split()
        return self._formatted_words_list_memo


class SplitForcedDictation(SplitDictation):
    """
    A SplitDictation with forced_dictation set to True, guaranteed to return
    a value for dictation, even if it must ignore an utterance-initial command
    from which to provide it.  
    """
    def __init__(self, name, registry=None, **kwargs):
        """

        :param string name: The name of this element, used as the keyname in the
            extras dictionary passed back to _process_recognition
        :param _Registry registry: The _Registry instance that determines what
            words form a command
        :param kwargs: Passed safely to `SplitDictation`
        
        """
        
        # ensure only one forced_dictation argument passed
        kwargs["forced_dictation"] = True
        SplitDictation.__init__(self, name=name, registry=registry, **kwargs)
