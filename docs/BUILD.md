# DocuRuleFix 打包指南

本文档介绍如何将 DocuRuleFix 打包成独立的可执行程序。

## 目录

- [自动构建 (推荐)](#自动构建-推荐)
- [Windows 平台](#windows-平台)
- [macOS 平台](#macos-平台)
- [常见问题](#常见问题)

---

## 自动构建 (推荐)

### 使用 GitHub Actions

项目配置了 GitHub Actions，可以自动构建所有平台的版本：

#### 触发自动构建

1. **推送到 main 分支**
   ```bash
   git push origin main
   ```
   自动构建所有平台版本，可在 Actions 页面下载

2. **创建发布版本**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   自动创建 Release 并附加构建产物

#### 下载构建产物

1. 访问 GitHub 仓库的 **Actions** 页面
2. 选择一个工作流运行
3. 在 **Artifacts** 部分下载对应平台的文件

#### 交叉编译说明

- **在 macOS 上构建 Windows 版本**: 使用 GitHub Actions (Windows runner)
- **在 Windows 上构建 macOS 版本**: 使用 GitHub Actions (macOS runner)
- **本地交叉编译**: 不推荐，建议使用 GitHub Actions

---

## Windows 平台

### 准备工作

1. **安装 Python 3.9+**
   - 下载: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **生成图标**
   ```bash
   python src/resources/icons/generate_icon.py
   ```

### 构建步骤

#### 方法一：使用构建脚本（推荐）

```bash
python build_windows.py
```

构建脚本会自动：
- 检查依赖和图标文件
- 清理旧的构建文件
- 执行 PyInstaller 构建
- 生成 NSIS 安装脚本
- 创建便携版目录

#### 方法二：使用 PyInstaller 直接构建

```bash
pyinstaller DocuRuleFix.spec
```

### 输出文件

构建完成后，在 `dist/` 目录下会生成：

```
dist/
├── DocuRuleFix.exe              # 单文件可执行程序
├── DocuRuleFix-Portable/        # 便携版目录
│   ├── DocuRuleFix.exe
│   ├── 启动 DocuRuleFix.bat
│   └── README.txt
└── DocuRuleFix-Setup.exe        # 安装程序（需要 NSIS）
```

### 创建安装程序（可选）

1. **下载并安装 NSIS**
   - https://nsis.sourceforge.io/

2. **编译安装脚本**
   - 右键点击 `installer.nsi`
   - 选择 "Compile NSIS Script"

---

## macOS 平台

### 准备工作

1. **安装 Python 3.9+**
   ```bash
   brew install python@3.11
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **生成图标**
   ```bash
   python src/resources/icons/generate_icon.py
   ```

### 构建步骤

#### 创建 .app Bundle

```bash
python build_macos_app.py
```

这会在 `build/` 目录下创建 `DocuRuleFix.app`。

### 使用 .app

```bash
# 直接运行
open build/DocuRuleFix.app

# 复制到 Applications 文件夹
cp -R build/DocuRuleFix.app /Applications/
```

### 创建 DMG 安装包（可选）

```bash
python build_macos_app.py --dmg
```

---

## 常见问题

### Q: Windows 构建后程序无法启动

**A:** 检查以下几点：
1. 确保已安装所有依赖
2. 检查图标文件是否存在
3. 尝试在 `DocuRuleFix.spec` 中设置 `console=True` 查看错误信息

### Q: macOS 图标在 Dock 中不显示

**A:** 需要安装 pyobjc-framework-Cocoa：
```bash
pip install pyobjc-framework-Cocoa
```

### Q: 打包后文件过大

**A:** 可以在 `.spec` 文件的 `excludes` 中添加更多不需要的模块，或使用 UPX 压缩。

### Q: 如何自定义图标

**A:**
1. 修改 `src/resources/icons/generate_icon.py` 中的 `create_icon()` 函数
2. 运行图标生成脚本
3. 重新构建应用

---

## 开发者信息

- **GitHub**: https://github.com/yourusername/DocuRuleFix
- **问题反馈**: https://github.com/yourusername/DocuRuleFix/issues
