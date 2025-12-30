# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller configuration file - DocuRuleFix

To build the executable:
    pyinstaller DocuRuleFix.spec

Or use the build script:
    python build_windows.py
"""

import os
import sys
from pathlib import Path

# Project root directory
project_root = Path(SPECPATH).parent.absolute()

# Icon path
icon_path = project_root / "src" / "resources" / "icons" / "DocuRuleFix.ico"

block_cipher = None


# Data files to include
datas = [
    # Config files
    (str(project_root / "config"), "config"),

    # Add other resources here if needed
    # (str(project_root / "resources"), "resources"),
]

# Hidden imports - for modules not detected automatically
hiddenimports = [
    # customtkinter related
    'customtkinter',
    'PIL._tkinter_finder',

    # python-docx related
    'docx',
    'docx.opc',
    'docx.oxml',
    'docx.oxml.xmlchemy',
    'docx.oxml.ns',
    'lxml',
    'lxml._elementpath',

    # Logging and config
    'loguru',
    'yaml',
    'jsonschema',

    # GUI components
    'gui.main_window',
    'gui.main_controller',
    'gui.components.file_selector',
    'gui.components.config_panel',
    'gui.components.progress_panel',
    'gui.components.results_panel',
    'gui.utils.theme_manager',
    'gui.utils.threading_helpers',

    # Core modules
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
        # Exclude unnecessary modules to reduce size
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
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
