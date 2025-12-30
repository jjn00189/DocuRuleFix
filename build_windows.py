#!/usr/bin/env python3
"""Windows 打包脚本

用于在 Windows 上构建 DocuRuleFix 的独立可执行文件。

使用方法:
    python build_windows.py

依赖:
    pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")

    try:
        import PyInstaller
        print(f"  ✓ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("  ✗ PyInstaller 未安装")
        print("  请运行: pip install pyinstaller")
        return False

    return True


def check_icon():
    """检查图标文件"""
    icon_path = Path(__file__).parent / "src" / "resources" / "icons" / "DocuRuleFix.ico"

    if icon_path.exists():
        print(f"  ✓ 图标文件: {icon_path}")
        return True
    else:
        print(f"  ✗ 图标文件不存在: {icon_path}")
        print("  请先运行图标生成脚本:")
        print("    python src/resources/icons/generate_icon.py")
        return False


def clean_build():
    """清理之前的构建结果"""
    print("\n清理之前的构建...")

    project_root = Path(__file__).parent
    build_dirs = [
        project_root / "build",
        project_root / "dist",
        project_root / "__pycache__",
    ]

    for dir_path in build_dirs:
        if dir_path.exists():
            print(f"  删除: {dir_path}")
            shutil.rmtree(dir_path)


def build_executable():
    """构建可执行文件"""
    print("\n开始构建...")

    project_root = Path(__file__).parent
    spec_file = project_root / "DocuRuleFix.spec"

    if not spec_file.exists():
        print(f"  ✗ 配置文件不存在: {spec_file}")
        return False

    # PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        str(spec_file),
    ]

    print(f"  执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            check=True,
            capture_output=False,
        )
        print("  ✓ 构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ 构建失败: {e}")
        return False


def create_installer_script():
    """创建简单的安装脚本 (NSIS)"""
    print("\n生成 NSIS 安装脚本...")

    project_root = Path(__file__).parent
    exe_path = project_root / "dist" / "DocuRuleFix.exe"

    if not exe_path.exists():
        print("  ✗ 可执行文件不存在，跳过安装脚本生成")
        return False

    nsis_script = f"""; DocuRuleFix 安装脚本
; 需要安装 NSIS: https://nsis.sourceforge.io/

!define APP_NAME "DocuRuleFix"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "DocuRuleFix"
!define APP_EXE "DocuRuleFix.exe"

; 现代 UI
!include "MUI2.nsh"

; general
Name "${{APP_NAME}}"
OutFile "Dist/${{APP_NAME}}-Setup-${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

; variables
Var StartMenuFolder

; interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "src\\\\resources\\\\icons\\\\DocuRuleFix.ico"
!define MUI_UNICON "src\\\\resources\\\\icons\\\\DocuRuleFix.ico"

; pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; languages
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; installer sections
Section "主程序" SecMain
    SectionIn RO

    SetOutPath "$INSTDIR"
    File "dist\\${{APP_EXE}}"

    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\\$StartMenuFolder\\${{APP_NAME}}.lnk" \\
        "$INSTDIR\\${{APP_EXE}}" "" \\
        "$INSTDIR\\${{APP_EXE}}" 0

    ; 创建桌面快捷方式
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" \\
        "$INSTDIR\\${{APP_EXE}}" "" \\
        "$INSTDIR\\${{APP_EXE}}" 0

    ; 写入注册表
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "version" "${{APP_VERSION}}"

    ; 写入卸载信息
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "DisplayVersion" "${{APP_VERSION}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" \\
        "NoRepair" 1
SectionEnd

; uninstaller section
Section "Uninstall"
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\uninstall.exe"
    Delete "$SMPROGRAMS\\$StartMenuFolder\\${{APP_NAME}}.lnk"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\$StartMenuFolder"
    RMDir "$INSTDIR"

    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
SectionEnd
"""

    nsis_file = project_root / "installer.nsi"
    nsis_file.write_text(nsis_script, encoding="utf-8")

    print(f"  ✓ 安装脚本已生成: {nsis_file}")
    print("\n  要创建安装程序，请:")
    print("    1. 下载并安装 NSIS: https://nsis.sourceforge.io/")
    print("    2. 右键点击 installer.nsi -> Compile NSIS Script")

    return True


def create_portable_package():
    """创建便携版压缩包"""
    print("\n创建便携版...")

    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    portable_dir = dist_dir / "DocuRuleFix-Portable"

    # 创建便携版目录
    portable_dir.mkdir(parents=True, exist_ok=True)

    # 复制可执行文件
    exe_src = dist_dir / "DocuRuleFix.exe"
    exe_dst = portable_dir / "DocuRuleFix.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        print(f"  ✓ 复制: DocuRuleFix.exe")

    # 创建启动脚本
    start_bat = portable_dir / "启动 DocuRuleFix.bat"
    start_bat.write_text('@echo off\r\nstart DocuRuleFix.exe\r\n', encoding="gbk")
    print(f"  ✓ 创建: 启动 DocuRuleFix.bat")

    # 创建说明文件
    readme_txt = portable_dir / "README.txt"
    readme_txt.write_text("""DocuRuleFix - 便携版

这是一个免安装的便携版本，直接运行 DocuRuleFix.exe 即可使用。

功能:
- Word 文档结构校验
- 自动修复常见错误
- 支持批量处理

使用方法:
1. 双击 "DocuRuleFix.exe" 或 "启动 DocuRuleFix.bat" 启动程序
2. 选择要处理的 Word 文档
3. 点击 "校验并修复" 按钮

版本: 1.0.0
主页: https://github.com/yourusername/DocuRuleFix
""", encoding="utf-8")
    print(f"  ✓ 创建: README.txt")

    print(f"\n  便携版已创建: {portable_dir}")
    print("  可以手动压缩该目录进行分发")


def main():
    """主函数"""
    print("=" * 60)
    print("DocuRuleFix Windows 构建脚本")
    print("=" * 60)

    # 检查依赖
    if not check_dependencies():
        return 1

    # 检查图标
    if not check_icon():
        return 1

    # 清理
    clean_build()

    # 构建
    if not build_executable():
        return 1

    # 创建安装脚本
    create_installer_script()

    # 创建便携版
    create_portable_package()

    print("\n" + "=" * 60)
    print("构建完成!")
    print("=" * 60)
    print("\n输出文件:")
    print("  - dist/DocuRuleFix.exe        (单文件可执行程序)")
    print("  - dist/DocuRuleFix-Portable/  (便携版目录)")
    print("  - installer.nsi               (NSIS 安装脚本)")
    print("\n可以直接运行 DocuRuleFix.exe 进行测试")

    return 0


if __name__ == "__main__":
    sys.exit(main())
