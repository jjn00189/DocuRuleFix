# DocuRuleFix - Word 文档处理工具

一个跨平台的 Python GUI 工具，支持多种规则对 Word 文档进行批量处理。

## 功能特性

- **三行一组结构校验**：校验文档是否符合"标题行 + URL行 + 图片行"的循环结构
- **损坏文档修复**：自动跳过损坏的图片引用（如 `../NULL`），能够处理损坏的 Word 文档
- **规则系统**：可扩展的规则架构，支持自定义规则
- **批量处理**：支持单文件和批量文件处理，可跳过损坏文档继续处理
- **自动修复**：支持自动修复常见的文档格式问题
- **跨平台**：支持 Windows 和 macOS

## 技术栈

- Python 3.13.0
- CustomTkinter（GUI框架）
- python-docx（Word文档操作）
- PyInstaller（打包）

## 安装

### 1. 克隆仓库

```bash
cd /path/to/DocuRuleFix
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

### GUI 界面（推荐）

```bash
python run_gui.py
```

GUI 功能：
- 拖拽 .docx 文件到窗口
- 选择标题模式（标准/精简）
- 配置处理选项（自动修复、创建备份、跳过损坏）
- 实时查看处理进度和日志
- 按类型分组显示错误
- 导出错误报告（JSON/CSV）
- 深色/浅色主题切换

**注意**：GUI 需要 tkinter 支持。如果启动失败，请安装：
- macOS: `brew install python-tk`
- Ubuntu: `sudo apt-get install python3-tk`
- Windows: 通常已包含在 Python 安装中

### 命令行使用

```bash
# 仅校验文档
python main.py path/to/document.docx

# 校验并自动修复
python main.py path/to/document.docx --fix

# 跳过损坏的文档（适用于批量处理）
python main.py path/to/document.docx --skip-corrupted
```

### Python 代码使用

```python
from src.core.rule_engine import RuleEngine
from src.core.document_processor import DocumentProcessor, CorruptedDocumentError
from src.rules.structure_rules import ThreeLineGroupValidationRule

# 创建规则引擎
rule_engine = RuleEngine()

# 注册规则（标准模式或精简模式）
rule = ThreeLineGroupValidationRule(title_mode="2")  # "1"=标准, "2"=精简
rule_engine.register_rule(rule)

# 创建文档处理器
processor = DocumentProcessor(rule_engine, create_backup=True)

# 仅校验
result = processor.validate_only("test.docx")
print(result.message)

# 处理文档
result = processor.process("test.docx", fix_errors=True)
print(result.message)

# 跳过损坏的文档
try:
    result = processor.validate_only("test.docx", skip_corrupted=True)
except CorruptedDocumentError as e:
    print(f"跳过损坏文档: {e.file_path}")
```

## 三行一组结构校验规则

文档按每3行一组的循环结构处理：

### 第1行（标题行）
- 格式：`序号+分隔符(.|,|)+内容`
- **标准模式** (`title_mode="1"`)：必须包含 `.` `_` `：` 三个字符
  - 舆论场（`.` 到 `_` 之间）
  - 来源（`_` 到 `：` 之间）
  - 标题（`：` 之后）
- **精简模式** (`title_mode="2"`)：只需 `序号.内容` 格式

### 第2行（URL行）
- 必须是有效的URL格式

### 第3行（图片行）
- 只能包含图片，不能有任何文字或空格

## 损坏文档修复

程序内置了对损坏 Word 文档的支持，能够自动跳过损坏的图片引用（如 `Target="../NULL"`），这些文档在 Word 中可以正常打开，但 python-docx 默认无法处理。

## 项目结构

```
DocuRuleFix/
├── src/
│   ├── core/              # 核心业务逻辑
│   ├── rules/             # 规则定义
│   ├── config/            # 配置管理
│   ├── gui/               # GUI界面
│   ├── utils/             # 工具函数（含docx补丁）
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
- [x] 损坏文档支持
- [x] GUI界面
- [ ] 其他规则类型
- [ ] 打包发布

## 许可证

MIT License
