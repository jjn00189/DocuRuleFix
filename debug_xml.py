#!/usr/bin/env python3
"""调试脚本：直接查看 XML 结构"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from docx import Document

try:
    # 加载文档
    doc = Document("/Users/jingjianan/workspace/project/jjn/DocuRuleFix/tests/1_fixed.docx")

    # 获取第13行（第4组图片行）- 索引12
    para = doc.paragraphs[12]

    print("="*60)
    print(f"段落 13 (第4组图片行) 分析")
    print("="*60)
    print(f"paragraph.runs 数量: {len(para.runs)}")
    print()

    # 查看 paragraph._element 直接访问 XML
    p_element = para._element
    print("直接访问 XML 元素:")

    # 直接打印 XML
    xml_str = p_element.xml
    print(f"  XML 长度: {len(xml_str)}")
    print()

    # 查找所有包含 graphic 或 pic 的行
    print("  查找图片相关元素:")
    if 'drawing' in xml_str or 'graphic' in xml_str or 'pic:' in xml_str:
        import re

        # 查找 extent
        extents = re.findall(r'<wp:extent[^>]*cy=["\'](\d+)["\'][^>]*>', xml_str)
        print(f"  找到 {len(extents)} 个 extent:")
        for i, cy in enumerate(extents):
            print(f"    extent[{i}]: cy={cy}")

        # 查找 docPr
        docPrs = re.findall(r'<wp:docPr[^>]*name=["\']([^"\']+)["\'][^>]*>', xml_str)
        print(f"  找到 {len(docPrs)} 个 docPr:")
        for i, name in enumerate(docPrs):
            print(f"    docPr[{i}]: name={name}")

    # 查找所有 w:r 子元素
    print()
    print("  查找子元素 w:r:")
    # 直接遍历子元素
    child_count = 0
    for child in p_element:
        child_count += 1
        tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        print(f"    子元素 {child_count}: {tag_name}")

    print()
    print("="*60)
    print("对比 paragraph.runs 与直接 XML 访问")
    print("="*60)
    print(f"paragraph.runs 长度: {len(para.runs)}")
    print(f"XML 子元素数量: {child_count}")

except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
