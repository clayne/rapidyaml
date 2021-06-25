# To make this file known to Qt Creator using:
# Tools > Options > Debugger > Locals & Expressions > Extra Debugging Helpers
# Any contents here will be picked up by GDB, LLDB, and CDB based
# debugging in Qt Creator automatically.


# Example to display a simple type
# template<typename U, typename V> struct MapNode
# {
#     U key;
#     V data;
# }
#
# def qdump__MapNode(d, value):
#    d.putValue("This is the value column contents")
#    d.putExpandable()
#    if d.isExpanded():
#        with Children(d):
#            # Compact simple case.
#            d.putSubItem("key", value["key"])
#            # Same effect, with more customization possibilities.
#            with SubItem(d, "data")
#                d.putItem("data", value["data"])

# Check http://doc.qt.io/qtcreator/creator-debugging-helpers.html
# for more details or look at qttypes.py, stdtypes.py, boosttypes.py
# for more complex examples.


import dumper
#from dumper import Dumper, Value, Children, SubItem
#from dumper import SubItem, Children
from dumper import *


# adapted from dumper.py::Dumper::putCharArrayValue()
def get_str_value(d, value, limit=0):
    m_str = value["str"].pointer()
    m_len = value["len"].integer()
    if limit == 0:
        limit = d.displayStringLimit
    elided, shown = d.computeLimit(m_len, limit)
    mem = bytes(d.readRawMemory(m_str, shown))
    return mem.decode('utf8'), m_len


def __display_csubstr(d, value, limit=0):
    m_str, m_len = get_str_value(d, value)
    d.putValue(f'\'{m_str}\'  [len={m_len}]')
    return m_str, m_len


def qdump__c4__csubstr(d, value):
    m_str, m_len = __display_csubstr(d, value)
    d.putExpandable()
    if d.isExpanded():
        with Children(d):
            ct = d.createType('char')
            for i in range(m_len):
                d.putSubItem(m_len, d.createValue(value["str"].pointer() + i, ct))
            d.putSubItem("len", value["len"])
            d.putPtrItem("str", value["str"].pointer())


def qdump__c4__substr(d, value):
    qdump__c4__csubstr(d, value)


def qdump__c4__basic_substring(d, value):
    qdump__c4__csubstr(d, value)


def qdump__c4__yml__NodeScalar(d, value):
    alen = value["anchor"]["len"].integer()
    tlen = value["tag"   ]["len"].integer()
    m_str, m_len = get_str_value(d, value["scalar"])
    if alen == 0 and tlen == 0:
        d.putValue(f'\'{m_str}\'')
    elif alen == 0 and tlen > 0:
        d.putValue(f'\'{m_str}\' [T-]')
    elif alen > 0 and tlen == 0:
        d.putValue(f'\'{m_str}\' [-A]')
    elif alen > 0 and tlen > 0:
        d.putValue(f'\'{m_str}\' [TA]')
    d.putExpandable()
    if d.isExpanded():
        with Children(d):
            d.putSubItem("[scalar]", value["scalar"])
            if tlen > 0:
                d.putSubItem("[tag]", value["tag"])
            if alen > 0:
                d.putSubItem("[anchor]", value["anchor"])


def _format_enum_value(int_value, enum_map):
    str_value = enum_map.get(int_value, None)
    display = f'{int_value}' if str_value is None else f'{str_value} ({int_value})'
    return display


def _c4bit(*ints):
    ret = 0
    for i in ints:
        ret |= 1 << i
    return ret


node_types = {
    0: "NOTYPE",
    _c4bit(0): "VAL"     ,
    _c4bit(1): "KEY"     ,
    _c4bit(2): "MAP"     ,
    _c4bit(3): "SEQ"     ,
    _c4bit(4): "DOC"     ,
    _c4bit(5,3): "STREAM",
    _c4bit(6): "KEYREF"  ,
    _c4bit(7): "VALREF"  ,
    _c4bit(8): "KEYANCH" ,
    _c4bit(9): "VALANCH" ,
    _c4bit(10): "KEYTAG" ,
    _c4bit(11): "VALTAG" ,
    _c4bit(1,0): "KEYVAL",
    _c4bit(1,3): "KEYSEQ",
    _c4bit(1,2): "KEYMAP",
    _c4bit(4,2): "DOCMAP",
    _c4bit(4,3): "DOCSEQ",
    _c4bit(4,0): "DOCVAL",
}
node_types_rev = {v: k for k, v in node_types.items()}


def _node_type_has_all(node_type_value, type_name):
    exp = node_types_rev[type_name]
    return (node_type_value & exp) == exp


def _node_type_has_any(node_type_value, type_name):
    exp = node_types_rev[type_name]
    return (node_type_value & exp) != 0


def qdump__c4__yml__NodeType_e(d, value):
    v = _format_enum_value(value.integer(), node_types)
    d.putValue(v)


def qdump__c4__yml__NodeType(d, value):
    qdump__c4__yml__NodeType_e(d, value["type"])


def qdump__c4__yml__NodeData(d, value):
    ty = _format_enum_value(value.integer(), node_types)
    t = value["m_type"]["type"].integer()
    k = value["m_key"]["scalar"]
    v = value["m_val"]["scalar"]
    sk, lk = get_str_value(d, k)
    sv, lv = get_str_value(d, v)
    if _node_type_has_all(t, "KEYVAL"):
        d.putValue(f"'{sk}': '{sv}' | {ty}")
    elif _node_type_has_any(t, "KEY"):
        d.putValue(f"'{sk}': | {ty}")
    elif _node_type_has_any(t, "VAL"):
        d.putValue(f"'{sv}' | {ty}")
    else:
        d.putValue(f"{ty}")
    d.putExpandable()
    if d.isExpanded():
        with Children(d):
            d.putSubItem("m_type", value["m_type"])
            if _node_type_has_any(t, "KEY"):
                d.putSubItem("m_key", value["m_key"])
            if _node_type_has_any(t, "VAL"):
                d.putSubItem("m_val", value["m_val"])
            _dump_node_index(d, "m_parent", value)
            _dump_node_index(d, "m_first_child", value)
            _dump_node_index(d, "m_last_child", value)
            _dump_node_index(d, "m_next_sibling", value)
            _dump_node_index(d, "m_prev_sibling", value)


def _dump_node_index(d, name, value):
    if int(value[name].integer()) == 18446744073709551615:
        pass
        #with SubItem(d, name):
        #    d.putValue("-")
    else:
        d.putSubItem(name, value[name])



# c4::yml::Tree
def qdump__c4__yml__Tree(d, value):
    m_size = value["m_size"].integer()
    m_cap = value["m_cap"].integer()
    d.putItemCount(m_size)
    if d.isExpanded():
        #d.putArrayData(value["m_buf"], m_size, value["m_buf"].dereference())
        with Children(d):
            with SubItem(d, f"[nodes]"):
                d.putItemCount(m_size)
                d.putArrayData(value["m_buf"].pointer(), m_size, value["m_buf"].type.dereference())
            d.putPtrItem("m_buf", value["m_buf"].pointer())
            d.putIntItem("m_size", value["m_size"])
            d.putIntItem("m_cap (capacity)", value["m_cap"])
            d.putIntItem("[slack]", m_cap - m_size)
            d.putIntItem("m_free_head", value["m_free_head"])
            d.putIntItem("m_free_tail", value["m_free_tail"])