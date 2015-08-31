import re

import six

from dragonfly import CompoundRule, Dictation, Function, ActionBase
# locate DictationContainerBase
import dragonfly.engines
base_dictation = getattr(dragonfly.engines, "dictation_base", None)
if base_dictation:
    from dragonfly.engines.dictation_base import DictationContainerBase
elif getattr(dragonfly.engines, "base", None):
    from dragonfly.engines.base import DictationContainerBase
else:
    print ("Cannot locate DictationContainerBase in either"
           "dragonfly.engines.dictation_base or dragonfly.engines.base")
    raise ImportError

from dragonfluid._elements import SplitDictation, SplitForcedDictation
from dragonfluid._support import _first_not_none, _safe_kwargs


class _RegistryRule(CompoundRule):
    def __init__(self, **kwargs):
        """kwargs passed to CompoundRule"""
        _safe_kwargs(CompoundRule.__init__, self, **kwargs)


class RegisteredRule(_RegistryRule):
    """
    A rule that can undergo `registration <registration>` to allow its command
    to be noticed in the middle of an utterance, allowing other commands to
    pass off to this rule. It must be added to a `RegistryGrammar`, such as the
    `GlobalRegistry`, for the registration to actually be performed. Otherwise,
    it acts like a normal CompoundRule_. 
    """    
    
    _is_registered = True # requests registration support
 
    # memoize variables
    _determined_intros = None
    _determined_partials = None
    
    def __init__(self, intros=None, intros_spec=None, **kwargs):
        """
        For information regarding ``intros`` and ``intros_spec``, refer to the
        `intros documentation <intros>`.
        
        :param intros: If None, the command `intros <intros>`
            will be automatically determined from the spec, otherwise any string
            provided, by itself or in a list, will be registered as an intro of
            the command. If supplied, overrides any provided ``intros_spec``.
        :type intros: string, string list, or None
        :param string intros_spec: If supplied, will be parsed to obtained the
            intros for the command, similar in manner to how spec is parsed.
        :param \*\*kwargs: passed safely to CompoundRule_
        
        """
        self._intros = _first_not_none(intros, getattr(self, "intros", None))
        if isinstance(self._intros, six.string_types):
                self._intros = [self._intros]
        self._intros_spec = _first_not_none(intros_spec, getattr(self, "intros_spec", None))
        
        # avoid duplicate processing to speed load time
        if not isinstance(self, FluidRule):
            _RegistryRule.__init__(self, **kwargs)


class ContinuingRule(_RegistryRule):
    """
    A rule that automatically looks for :term:`embedded commands <embedded
    command>` and :term:`chains <chaining>` to
    them. It must be added to a `RegistryGrammar`, such as the
    `GlobalRegistry` to enable all features.
    """    
    def __init__(self, **kwargs):
        """        
        :param \*\*kwargs: passed safely to CompoundRule_
       
        """
        _spec = _first_not_none(kwargs.get("spec"), self.spec)
        _extras = _first_not_none(kwargs.get("extras"), getattr(self, "extras", None))

        kwargs["spec"], kwargs["extras"] = self._alter_rule(_spec, _extras)
        _RegistryRule.__init__(self, **kwargs)


    def _alter_rule(self, _spec, _extras):
        if False == getattr(self, "_autoFluidRule_altered", False):
            self._autoFluidRule_altered = True
        else:
            return # don't alter multiple times

        _original_process_recognition = self._process_recognition.im_func
        
        def _extraadded_flowfull_process_recognition(self, node, extras):
            _original_process_recognition(self, node, extras)
            if self._flow_element in extras: # optional, so maybe not
                extras[self._flow_element].mimic_full()
            
        def _flowcommand_process_recognition(self, node, extras):
            _original_process_recognition(self, node, extras)
            if self._flow_element in extras: # perhaps optional
                extras[self._flow_element].mimic_command()
            
        def _autoflowcommand_process_recognition(self, node, extras):
            flow_element = extras.get(self._flow_element, None)
            if flow_element:
                # replace the extra transparently with exactly what a user
                # expects from a Dictation element, a normal container rather
                # than our meta-container
                extras[self._flow_element] = flow_element.dictation_container_trans
            _original_process_recognition(self, node, extras)
            if flow_element:
                flow_element.mimic_command()          

        _extras = dict((extra.name, extra) for extra in _extras)
        match = re.match(
            r"""
            .*                      # any beginning
            \[?\s*                  # possibly optional extra
            <(?P<final_extra>.*?)>  # capture extra name as final_extra
            \s*\]?\s*               # with possible end optional indicator
            $                       # at the very end of spec
            """, _spec, re.VERBOSE)

        if match: # spec ends with an extra
            extra_name = match.group("final_extra")
            if isinstance(_extras[extra_name], SplitDictation):
                self._process_recognition = _flowcommand_process_recognition.__get__(self)
            elif isinstance(_extras[extra_name], Dictation):
                _extras[extra_name] = SplitForcedDictation(extra_name)
                self._process_recognition = _autoflowcommand_process_recognition.__get__(self)
            else:
                _spec, extra_name = self._add_flow_element(_spec, _extras, _extraadded_flowfull_process_recognition)
        else:
            _spec, extra_name = self._add_flow_element(_spec, _extras, _extraadded_flowfull_process_recognition)
        
        self._flow_element = extra_name
        
        _extras = _extras.values()
        return _spec, _extras
    
    def _add_flow_element(self, _spec, _extras, _extraadded_flowfull_process_recognition):
        extra_name = "fluid"
        while extra_name in _extras:
            extra_name += "fluid"
        _spec += " [<" + extra_name + ">]"
        _extras[extra_name] = SplitDictation(extra_name)
        self._process_recognition = _extraadded_flowfull_process_recognition.__get__(self)
        return _spec, extra_name


class FluidRule(RegisteredRule, ContinuingRule):
    """
    A FluidRule is both a `RegisteredRule` and a `ContinuingRule`, meaning it
    can be :term:`chained <chaining>` to from other commands, and then chain off
    to further commands. This is the most common case, for general use unless
    you have specific needs. These always attempt to chain automatically.

    It must be added to a `RegistryGrammar`, such as the `GlobalRegistry`,
    to enabled all features.
    """
    def __init__(self, **kwargs):
        """        
        :param \*\*kwargs: passed to `ContinuingRule` and `RegisteredRule`
        """

        # setup RegisteredRule first, as it only needs the intros fully
        # determined and ContinuingRule does not alter the intros, whereas
        # ContinuingRule alters the extras in necessary ways, so these
        # changes must not be undone by the original extras value in kwargs,
        # which would occur RegisteredRule was called after.
        RegisteredRule.__init__(self, **kwargs)
        ContinuingRule.__init__(self, **kwargs)


class _BaseQuickRules(object):
    def __init__(self, grammar):
        self._grammer = grammar
    def add_rule(self, rule):
        self._grammer.add_rule(rule)


class QuickFluidRule(FluidRule):
    """
    A shortcut to assign an action_ to a spec.
    
    Example::
    
        rule = QuickFluidRule("press home key", Key("home"))
        
    """
    _next_unique_id = 1

    def __init__(self, spec, action, args={}, **kwargs):
        """
        
        :param string spec: The spec for this command, from which `intros
            <intros>` will be determined.
        :param action: The action to be executed when this
            command is said.
        :type action: a dragonfly action_
        :param dict args: Provides a way to add to or modify the extras
            dictionary. The args dictionary has keys of name strings, items of
            function callbacks. The callbacks are supplied a single parameter
            of a dictionary of extras, and their return value is assigned to
            the extra named by the key. When the ``action`` is executed, it
            will then have these final values available to it.
        :param \*\*kwargs: Passed to `FluidRule`, except ``"name"`` and ``"spec"``
            ignored.
        
        
        """
        if isinstance(action, ActionBase) or not six.callable(action):
            self.action = action
            self._is_call = False
        else:
            self.action = Function(action)
            self._is_call = True

        self.args = args
        kwargs["spec"] = spec
        kwargs["name"] = self._autogenerate_name(spec)
        FluidRule.__init__(self, **kwargs)
    
    def _autogenerate_name(self, spec):
        id_string = str(QuickFluidRule._next_unique_id)
        QuickFluidRule._next_unique_id += 1
        return "quickFluidRule_" + spec + "_id" + id_string
            
    def _process_recognition(self, node, extras):
        if self._is_call:
            format_candidates = [(name, extra) for name, extra in extras.items() if name not in self.args.keys()]
            for name, extra in format_candidates:
                if isinstance(extra, DictationContainerBase):
                    extras[name] = extra.format()
        for name, value_callback in self.args.items():
            extras[name] = value_callback(extras)
        self.action.execute(extras)


class QuickFluidRules(_BaseQuickRules):
    """
    Used like a MappingRule_ but results in `FluidRule`'s rather than simple
    CompoundRule_\ 's.
    
    The ``mapping`` attribute is extended. In addition to the normal key/value
    pairs of spec/action, a value may also be a list or tuple whose first
    element is the usual action, and whose second element is a dict of
    parameters to be passed as \*\*kwargs to `QuickFluidRule`.
    """
    def __init__(self, grammar):
        """
        Not usually called directly, but rather via `ActiveGrammarRule`.
        
        :param grammar: The Grammar to add rules to, generally a
            `RegistryGrammar` such as the `GlobalRegistry`.
        """
        _BaseQuickRules.__init__(self, grammar)
        for spec, entry in self.mapping.items():
            kwargs = {}
            kwargs["extras"] = getattr(self, "extras", None)
            kwargs["defaults"] = getattr(self, "defaults", None)
            kwargs["context"] = getattr(self, "context", None)            
            if isinstance(entry, (list, tuple)):             
                action = entry[0]
                kwargs.update(entry[1])
            else:
                action = entry
            self.add_rule(QuickFluidRule(spec, action, **kwargs))
