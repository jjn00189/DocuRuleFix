"""python-docx 库的补丁模块

修复 python-docx 无法处理损坏的文档引用（如 ../NULL）的问题
"""

from docx.opc.pkgreader import _SerializedRelationships, _SerializedRelationship
from docx.opc.oxml import parse_xml


def load_from_xml_v2(baseURI, rels_item_xml):
    """
    修复版本的 load_from_xml 函数

    返回从 *rels_item_xml* 加载的 |_SerializedRelationships| 实例。
    如果 *rels_item_xml* 为 |None|，返回空集合。

    修复内容：跳过 Target 为 '../NULL' 或 'NULL' 的损坏引用
    """
    srels = _SerializedRelationships()
    if rels_item_xml is not None:
        rels_elm = parse_xml(rels_item_xml)
        for rel_elm in rels_elm.Relationship_lst:
            # 跳过损坏的引用
            if rel_elm.target_ref in ('../NULL', 'NULL'):
                continue
            srels._srels.append(_SerializedRelationship(baseURI, rel_elm))
    return srels


def apply_patch():
    """应用补丁到 python-docx 库"""
    _SerializedRelationships.load_from_xml = load_from_xml_v2


# 自动应用补丁（当模块被导入时）
apply_patch()
