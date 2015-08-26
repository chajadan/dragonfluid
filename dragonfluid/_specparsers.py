import itertools
import xml.dom.minidom

from dragonfluid._support import _rstrip_from, _single_spaces_and_trimmed

def _xmlize_spec(spec):
    spec = spec.replace("<", "{") # "escape" angle brackets
    spec = spec.replace(">", "}")

    # optional elements might contain alternatives, e.g., "a [long|short] rule"
    spec = spec.replace("[", "<optional><alternatives><alternative>")
    spec = spec.replace("]", "</alternative></alternatives></optional>")
    
    spec = spec.replace("(", "<alternatives><alternative>")
    spec = spec.replace(")", "</alternative></alternatives>")
    spec = spec.replace("|", "</alternative><alternative>")

    # wrap with alternatives as root, in case of embedded top-level option
    # e.g. "command one | command two"
    spec = "<alternatives><alternative>" + spec + "</alternative></alternatives>"    
    return spec


class _XmlSpecNode:
    TEXT_NODE = 3

    def __init__(self, node):
        self.node = xml.dom.minidom.parseString(node)

    def get_intros(self):
        intros = [""]
        for child in self.node.firstChild.childNodes:
            tag = child.nodeName
            if child.nodeType == _XmlSpecNode.TEXT_NODE:
                new_intros = [child.nodeValue]
            elif tag == "alternatives":
                new_intros = _AlternativesNode(child.toxml()).get_intros()
            elif tag == "optional":
                new_intros = [""] + _XmlSpecNode(child.toxml()).get_intros()                        
            else:
                new_intros = _XmlSpecNode(child.toxml()).get_intros()
            new_intros = itertools.product(intros, new_intros)
            # replace intros with a cartesian product by new_intros
            intros = [" ".join(parts) for parts in new_intros]
        intros = map(_rstrip_from, intros, "{" * len(intros))
        intros = map(_single_spaces_and_trimmed, intros)
        intros = filter(None, intros) # remove empty intros
        return intros


class _XmlSpecParser(_XmlSpecNode):
    ""
    def __init__(self, spec):
        self._xml_spec = _xmlize_spec(spec)
        self.node = xml.dom.minidom.parseString(self._xml_spec)


class _AlternativesNode(_XmlSpecNode):
    def get_intros(self):
        intros = []
        for child in self.node.firstChild.childNodes:
            assert child.nodeName == "alternative" # will only have <alternative> children
            intros += _XmlSpecNode(child.toxml()).get_intros()
        return intros
