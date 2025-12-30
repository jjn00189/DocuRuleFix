# DocuRuleFix 打包指南

本文档介绍如何将 DocuRuleFix 打包成独立的可执行程序。

**当前支持平台**: Windows

## 目录

- [自动构建 (推荐)](#自动构建-推荐)
- [Windows 本地构建](#windows-本地构建)
- [发布版本](#发布版本)
- [常见问题](#常见问题)

---

## 自动构建 (推荐)

### 使用 GitHub Actions

项目配置了 GitHub Actions，可以自动构建 Windows 版本：

#### 触发自动构建

1. **推送到 main 分支**
   ```bash
   git push origin main
   ```
   自动构建 Windows 版本，可在 Actions 页面下载

2. **手动触发构建**
   - 访问 GitHub 仓库的 **Actions** 页面
   - 选择 **Build Windows** 工作流
   - 点击 **Run workflow**

#### 下载构建产物

1. 访问 GitHub 仓库的 **Actions** 页面
2. 选择一个工作流运行
3. 在 **Artifacts** 部分下载 `DocuRuleFix-Windows`

---

## Windows 本地构建

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

## 发布版本

### 创建 Git Tag

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签到 GitHub
git push origin v1.0.0
```

### 自动发布

推送 tag 后，GitHub Actions 会自动：
1. 在 Windows 上构建可执行文件
2. 创建 Release
3. 附加构建产物到 Release

### 下载发布版本

访问 GitHub 仓库的 **Releases** 页面下载：
- `DocuRuleFix.exe` - 单文件可执行程序
- `DocuRuleFix-Portable.zip` - 便携版压缩包
- `installer.nsi` - NSIS 安装脚本

---

## 常见问题

### Q: Windows 构建后程序无法启动

**A:** 检查以下几点：
1. 确保已安装所有依赖
2. 检查图标文件是否存在
3. 尝试在 `DocuRuleFix.spec` 中设置 `console=True` 查看错误信息

### Q: 打包后文件过大

**A:** 可以在 `.spec` 文件的 `excludes` 中添加更多不需要的模块，或使用 UPX 压缩。

### Q: 如何自定义图标

**A:**
1. 修改 `src/resources/icons/generate_icon.py` 中的 `create_icon()` 函数
2. 运行图标生成脚本
3. 重新构建应用

### Q: 在 macOS 上如何构建 Windows 版本

**A:** 使用 GitHub Actions 自动构建，或者找一个 Windows 系统进行本地构建。

---

## 开发者信息

- **GitHub**: https://github.com/yourusername/DocuRuleFix
- **问题反馈**: https://github.com/yourusername/DocuRuleFix/issues
