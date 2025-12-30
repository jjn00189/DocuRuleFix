# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件 - DocuRuleFix

用于将 DocuRuleFix 打包成独立的可执行文件。
使用方法:
    pyinstaller DocuRuleFix.spec

或者使用构建脚本:
    python build_windows.py
"""

import os
import sys
from pathlib import Path

# 项目根目录
project_root = Path(SPECPATH).absolute

# 图标路径
icon_path = project_root / "src" / "resources" / "icons" / "DocuRuleFix.ico"

block_cipher = None


# 收集所有需要的数据文件
datas = [
    # 配置文件
    (str(project_root / "config"), "config"),

    # 如果有其他资源文件，添加到这里
    # (str(project_root / "resources"), "resources"),
]

# 隐藏导入 - 解决一些模块无法被自动检测的问题
hiddenimports = [
    # customtkinter 相关
    'customtkinter',
    'PIL._tkinter_finder',

    # python-docx 相关
    'docx',
    'docx.opc',
    'docx.oxml',
    'docx.oxml.xmlchemy',
    'docx.oxml.ns',
    'lxml',
    'lxml._elementpath',

    # 日志和配置
    'loguru',
    'yaml',
    'jsonschema',

    # GUI 组件
    'gui.main_window',
    'gui.main_controller',
    'gui.components.file_selector',
    'gui.components.config_panel',
    'gui.components.progress_panel',
    'gui.components.results_panel',
    'gui.utils.theme_manager',
    'gui.utils.threading_helpers',

    # 核心模块
    'core.document_processor',
    'core.rule_engine',
    'rules.base_rule',
    'rules.structure_rules',
    'gui.utils.docx_patch',
]


a = Analysis(
    [str(project_root / "src" / "gui" / "app.py")],
    pathex=[str(project_root), str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'tkinter.test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocuRuleFix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
