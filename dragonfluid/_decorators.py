from dragonfluid._grammars import RegistryGrammar
from dragonfluid._elements import _RegistryElement
from dragonfluid._rules import _BaseQuickRules

# decorator
def ActiveGrammarRule(grammar):
    """
    A rule class decorator to automatically instantiate and add the rule to the
    grammar specified.
    
    Example:
    
    ::
    
        from dragonfly import Grammar, CompoundRule, MappingRule
        from dragonfluid import ActiveGrammarRule, FluidRule, QuickFluidRules
        
        my_grammar_instance = Grammar("my_grammar")
        
        @ActiveGrammarRule(my_grammar_instance)
        class MyRule(CompoundRule):
            pass
        
        @ActiveGrammarRule(my_grammar_instance)
        class MyRules(MappingRule):
            pass
        
        @ActiveGrammarRule(my_grammar_instance)
        class MyFluidRule(FluidRule):
            pass
                
        @ActiveGrammarRule(my_grammar_instance)
        class MyQuickRules(QuickFluidRules):
            pass

    """
    
    def AddToGrammar(rule_class):
        if isinstance(grammar, RegistryGrammar):
            if getattr(rule_class, "extras", None):
                registry_extras = [extra for extra in rule_class.extras 
                                   if isinstance(extra, _RegistryElement)]
                for extra in registry_extras:
                    if extra._registry is None:
                        extra.registry = grammar.registry
                
        if issubclass(rule_class, _BaseQuickRules):
            rule_class(grammar)
        else:
            grammar.add_rule(rule_class())
    return AddToGrammar