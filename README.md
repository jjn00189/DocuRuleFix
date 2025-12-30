# DocuRuleFix - Word 文档处理工具

一个跨平台的 Python GUI 工具，支持多种规则对 Word 文档进行批量处理。

## 功能特性

- **三行一组结构校验**：校验文档是否符合"标题行 + URL行 + 图片行"的循环结构
- **规则系统**：可扩展的规则架构，支持自定义规则
- **批量处理**：支持单文件和批量文件处理
- **自动修复**：支持自动修复常见的文档格式问题
- **跨平台**：支持 Windows 和 macOS

## 技术栈

- Python 3.8+
- CustomTkinter（GUI框架）
- python-docx（Word文档操作）
- PyInstaller（打包）

## 安装

### 1. 克隆仓库

```bash
cd /Users/jingjianan/workspace/project/jjn/DocuRuleFix
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

```bash
# 仅校验文档
python main.py path/to/document.docx

# 校验并自动修复
python main.py path/to/document.docx --fix
```

### Python 代码使用

```python
from src.core.rule_engine import RuleEngine
from src.core.document_processor import DocumentProcessor
from src.rules.structure_rules import ThreeLineGroupValidationRule

# 创建规则引擎
rule_engine = RuleEngine()

# 注册规则
rule = ThreeLineGroupValidationRule(title_mode="1")
rule_engine.register_rule(rule)

# 创建文档处理器
processor = DocumentProcessor(rule_engine, create_backup=True)

# 仅校验
result = processor.validate_only("test.docx")
print(result.message)

# 处理文档
result = processor.process("test.docx", fix_errors=True)
print(result.message)
```

## 三行一组结构校验规则

文档按每3行一组的循环结构处理：

### 第1行（标题行）
- 格式：`序号+分隔符(.|,|)+内容`
- 标准模式：必须包含 `.` `_` `：` 三个字符
  - 舆论场（`.` 到 `_` 之间）
  - 来源（`_` 到 `：` 之间）
  - 标题（`：` 之后）

### 第2行（URL行）
- 必须是有效的URL格式

### 第3行（图片行）
- 只能包含图片，不能有文字

## 项目结构

```
DocuRuleFix/
├── src/
│   ├── core/              # 核心业务逻辑
│   ├── rules/             # 规则定义
│   ├── config/            # 配置管理
│   ├── gui/               # GUI界面
│   ├── utils/             # 工具函数
│   └── models/            # 数据模型
├── config/                # 配置文件
├── tests/                 # 测试
├── main.py                # 应用入口
└── requirements.txt       # 依赖清单
```

## 开发计划

- [x] 项目初始化
- [x] 规则基类
- [x] 三行一组结构校验规则
- [x] 规则引擎
- [x] 文档处理器
- [ ] GUI界面
- [ ] 其他规则类型
- [ ] 打包发布

## 许可证

MIT License
