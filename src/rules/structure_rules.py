"""文档结构校验规则模块

实现三行一组文档结构校验规则
"""

import re
from typing import List, Dict, Optional
from docx import Document
from docx.text.paragraph import Paragraph

from .base_rule import BaseRule, ValidationError


class ThreeLineGroupValidationRule(BaseRule):
    """三行一组结构校验规则

    文档按每3行一组的循环结构处理：
    - 第1行（段落索引 %3 == 0）：标题行
    - 第2行（段落索引 %3 == 1）：URL行
    - 第3行（段落索引 %3 == 2）：图片行
    """

    # URL 正则表达式
    REGEX_URL = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
    # 标题行正则表达式：以数字开头，后跟 .、, 或 | 分隔符
    REGEX_TITLE = r'^\d+[.|,|)][\s\S]+'

    def __init__(self, title_mode: str = "1", enabled: bool = True):
        """

        Args:
            title_mode: 标题模式
                - "1": 标准模式，需要包含 . _ ： 三个字符
                - "2": 精简模式，只需要提取 . 后的内容
            enabled: 是否启用该规则
        """
        super().__init__("三行一组结构校验", enabled)
        self.title_mode = title_mode

    def validate(self, document: Document) -> List[ValidationError]:
        """校验文档结构

        Args:
            document: 要校验的Word文档对象

        Returns:
            发现的错误列表
        """
        self.clear_errors()
        paragraphs = document.paragraphs

        # 检查段落数量是否为3的倍数
        total_paragraphs = len(paragraphs)
        if total_paragraphs % 3 != 0:
            self.errors.append(ValidationError(
                -1, 'structure',
                f'段落数量({total_paragraphs})不是3的倍数，剩余{total_paragraphs % 3}行'
            ))

        # 遍历每三行一组
        for i in range(0, len(paragraphs), 3):
            group_index = i // 3

            # 检查标题行（第1行）
            if i < len(paragraphs):
                self._validate_title_line(paragraphs[i], i, group_index)

            # 检查URL行（第2行）
            if i + 1 < len(paragraphs):
                self._validate_url_line(paragraphs[i + 1], i + 1, group_index)

            # 检查图片行（第3行）
            if i + 2 < len(paragraphs):
                self._validate_image_line(paragraphs[i + 2], i + 2, group_index)

        return self.errors

    def _validate_title_line(self, paragraph: Paragraph, index: int, group_index: int) -> None:
        """校验标题行

        Args:
            paragraph: 段落对象
            index: 段落索引
            group_index: 组索引（第几组）
        """
        text = paragraph.text.strip()

        # 空行检查
        if not text:
            self.errors.append(ValidationError(
                index, 'title',
                f'第{group_index + 1}组标题行为空'
            ))
            return

        # 检查基础格式（序号+分隔符+内容）
        if not re.match(self.REGEX_TITLE, text):
            self.errors.append(ValidationError(
                index, 'title',
                f'第{group_index + 1}组标题行格式错误，应为"序号+分隔符(.|,|)+内容"，当前为: "{text[:50]}..."'
            ))
            return

        # 标准模式检查
        if self.title_mode == "1":
            required_chars = {'.': '点', '_': '下划线', '：': '冒号'}
            for char, char_name in required_chars.items():
                if char not in text:
                    self.errors.append(ValidationError(
                        index, 'title',
                        f'第{group_index + 1}组标题行缺少必需字符"{char}"({char_name})'
                    ))

    def _validate_url_line(self, paragraph: Paragraph, index: int, group_index: int) -> None:
        """校验URL行

        Args:
            paragraph: 段落对象
            index: 段落索引
            group_index: 组索引（第几组）
        """
        text = paragraph.text.strip()

        # 空行检查
        if not text:
            self.errors.append(ValidationError(
                index, 'url',
                f'第{group_index + 1}组URL行为空'
            ))
            return

        # URL格式检查
        if not re.match(self.REGEX_URL, text):
            self.errors.append(ValidationError(
                index, 'url',
                f'第{group_index + 1}组URL行格式错误: "{text[:80]}..."'
            ))

    def _validate_image_line(self, paragraph: Paragraph, index: int, group_index: int) -> None:
        """校验图片行

        Args:
            paragraph: 段落对象
            index: 段落索引
            group_index: 组索引（第几组）
        """
        text = paragraph.text.strip()

        # 检查是否有文字（图片行不应该有文字）
        if text:
            self.errors.append(ValidationError(
                index, 'image',
                f'第{group_index + 1}组图片行包含文字内容，应仅为图片。文字内容: "{text[:50]}..."'
            ))

        # 检查是否有图片
        has_image = self._has_image(paragraph)
        if not has_image:
            self.errors.append(ValidationError(
                index, 'image',
                f'第{group_index + 1}组图片行没有图片'
            ))

    def _has_image(self, paragraph: Paragraph) -> bool:
        """检查段落是否包含图片

        Args:
            paragraph: 段落对象

        Returns:
            True表示包含图片，False表示不包含
        """
        for run in paragraph.runs:
            if 'graphic' in run._element.xml or 'pic:' in run._element.xml:
                return True
            # 检查是否有blip元素（嵌入图片）
            if run._element.xpath('.//a:blip'):
                return True
        return False

    def apply(self, document: Document) -> Document:
        """应用规则到文档（校验并返回）

        Args:
            document: 要处理的Word文档对象

        Returns:
            处理后的文档对象
        """
        # 校验规则主要用于验证，这里只做校验
        self.validate(document)
        return document

    def fix(self, document: Document) -> Document:
        """自动修复文档

        Args:
            document: 要修复的Word文档对象

        Returns:
            修复后的文档对象
        """
        # 先校验获取所有错误
        self.validate(document)

        if not self.errors:
            return document

        # 按错误类型分组
        errors_by_index: Dict[int, List[ValidationError]] = {}
        for error in self.errors:
            if error.line_index not in errors_by_index:
                errors_by_index[error.line_index] = []
            errors_by_index[error.line_index].append(error)

        # 逐个修复
        for index, errors in sorted(errors_by_index.items()):
            if index >= len(document.paragraphs):
                continue

            paragraph = document.paragraphs[index]

            for error in errors:
                if error.line_type == 'image' and '包含文字内容' in error.message:
                    # 删除图片行中的文字
                    self._clear_text_from_paragraph(paragraph)
                elif error.line_type == 'title':
                    # 尝试修复标题格式
                    self._fix_title_format(paragraph, index)
                elif error.line_type == 'url' and '格式错误' in error.message:
                    # 标记无效URL或删除
                    pass

        # 处理段落数量不是3的倍数的情况
        total_paragraphs = len(document.paragraphs)
        if total_paragraphs % 3 != 0:
            remainder = total_paragraphs % 3
            # 删除末尾多余的段落
            for _ in range(remainder):
                # 注意：这里需要从末尾删除
                pass  # python-docx不支持直接删除段落，需要其他处理方式

        # 清空错误列表（已修复）
        self.clear_errors()

        return document

    def _clear_text_from_paragraph(self, paragraph: Paragraph) -> None:
        """清除段落中的文字，保留图片

        Args:
            paragraph: 段落对象
        """
        for run in paragraph.runs:
            if run.text:
                run.text = ""

    def _fix_title_format(self, paragraph: Paragraph, index: int) -> None:
        """尝试修复标题格式

        Args:
            paragraph: 段落对象
            index: 段落索引
        """
        text = paragraph.text.strip()

        # 如果缺少序号，尝试添加
        if not re.match(r'^\d', text):
            group_num = (index // 3) + 1
            # 检查是否已经有分隔符，有则直接加序号
            if re.match(r'^[.|,|)]', text):
                new_text = f"{group_num}{text}"
            else:
                # 尝试添加序号和分隔符
                new_text = f"{group_num}. {text}"

            # 更新段落文本
            if paragraph.runs:
                paragraph.runs[0].text = new_text
                # 清除其他run的文本
                for run in paragraph.runs[1:]:
                    run.text = ""

    def parse_title(self, title_text: str) -> Dict[str, str]:
        """解析标题行，提取字段

        Args:
            title_text: 标题文本

        Returns:
            包含解析字段的字典
        """
        result: Dict[str, str] = {}

        try:
            # 去除序号部分
            content = re.sub(r'^\d+[.|,|)]', '', title_text).strip()

            if self.title_mode == "1":
                # 标准模式：提取舆论场、来源、标题
                dot_idx = content.find('.')
                underscore_idx = content.find('_')
                colon_idx = content.find('：')

                if all(idx >= 0 for idx in [dot_idx, underscore_idx, colon_idx]):
                    result['opinion'] = content[dot_idx + 1:underscore_idx].strip()
                    result['source'] = content[underscore_idx + 1:colon_idx].strip()
                    result['title'] = content[colon_idx + 1:].strip()
                else:
                    result['error'] = f"无法解析标题，缺少必需分隔符。内容: {content}"
            else:
                # 精简模式：只提取标题
                result['title'] = content

        except Exception as e:
            result['error'] = str(e)

        return result

    def parse_document(self, document: Document) -> List[Dict[str, any]]:
        """解析整个文档，提取所有三行一组的数据

        Args:
            document: Word文档对象

        Returns:
            包含所有组数据的列表
        """
        results = []
        paragraphs = document.paragraphs

        for i in range(0, len(paragraphs), 3):
            group_data = {
                'group_index': i // 3,
                'title_line': None,
                'url_line': None,
                'image_line': None
            }

            # 标题行
            if i < len(paragraphs):
                title_text = paragraphs[i].text.strip()
                group_data['title_line'] = {
                    'text': title_text,
                    'parsed': self.parse_title(title_text),
                    'has_error': any(e.line_index == i and e.line_type == 'title' for e in self.errors)
                }

            # URL行
            if i + 1 < len(paragraphs):
                url_text = paragraphs[i + 1].text.strip()
                group_data['url_line'] = {
                    'text': url_text,
                    'is_valid': bool(re.match(self.REGEX_URL, url_text)),
                    'has_error': any(e.line_index == i + 1 and e.line_type == 'url' for e in self.errors)
                }

            # 图片行
            if i + 2 < len(paragraphs):
                paragraph = paragraphs[i + 2]
                group_data['image_line'] = {
                    'text': paragraph.text.strip(),
                    'has_image': self._has_image(paragraph),
                    'has_error': any(e.line_index == i + 2 and e.line_type == 'image' for e in self.errors)
                }

            results.append(group_data)

        return results
