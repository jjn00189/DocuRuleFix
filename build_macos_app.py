#!/usr/bin/env python3
"""Build macOS .app bundle for DocuRuleFix

This script creates a proper macOS application bundle that will display
the icon in the Dock and in Finder.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def build_app_bundle():
    """Build macOS .app bundle"""

    # Project root
    project_root = Path(__file__).parent

    # App bundle structure
    app_name = "DocuRuleFix"
    app_bundle = project_root / "build" / f"{app_name}.app"
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    # Clean existing build
    if app_bundle.exists():
        shutil.rmtree(app_bundle)

    # Create directory structure
    macos_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)

    # Copy icon
    icon_source = project_root / "src" / "resources" / "icons" / "DocuRuleFix.icns"
    icon_dest = resources_dir / "DocuRuleFix.icns"
    if icon_source.exists():
        shutil.copy2(icon_source, icon_dest)
        print(f"✓ Copied icon: {icon_dest}")
    else:
        print(f"✗ Icon not found: {icon_source}")
        return False

    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIconFile</key>
    <string>DocuRuleFix.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.docurulefix.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
"""

    plist_path = contents_dir / "Info.plist"
    plist_path.write_text(info_plist)
    print(f"✓ Created Info.plist: {plist_path}")

    # Create launcher script
    launcher_script = f"""#!/bin/bash
# Launcher script for {app_name}

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
VENV="$PROJECT_ROOT/../venv"
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
fi

# Run the application
cd "$PROJECT_ROOT"
exec python3 -m gui.main_window "$@"
"""

    launcher_path = macos_dir / app_name
    launcher_path.write_text(launcher_script)
    launcher_path.chmod(0o755)
    print(f"✓ Created launcher: {launcher_path}")

    # Copy PList (PkgInfo) file
    pkginfo_path = contents_dir / "PkgInfo"
    pkginfo_path.write_text("APPL????")
    print(f"✓ Created PkgInfo: {pkginfo_path}")

    print(f"\n✓ App bundle created: {app_bundle}")
    print(f"\nTo run the app:")
    print(f"  open {app_bundle}")
    print(f"\nTo move to Applications folder:")
    print(f"  cp -R {app_bundle} /Applications/")

    return True


def create_dmg():
    """Optional: Create a DMG installer"""
    project_root = Path(__file__).parent
    app_bundle = project_root / "build" / "DocuRuleFix.app"

    if not app_bundle.exists():
        print("✗ App bundle not found. Run build first.")
        return False

    dmg_path = project_root / "build" / "DocuRuleFix.dmg"

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    # Create DMG using hdiutil
    try:
        subprocess.run([
            'hdiutil', 'create',
            '-volname', 'DocuRuleFix',
            '-srcfolder', str(app_bundle.parent),
            '-ov', '-format', 'UDZO',
            str(dmg_path)
        ], check=True)
        print(f"✓ DMG created: {dmg_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create DMG: {e}")
        return False


if __name__ == "__main__":
    if build_app_bundle():
        print("\n" + "="*50)
        print("Build successful!")
        print("="*50)

        # Optionally create DMG
        if len(sys.argv) > 1 and sys.argv[1] == "--dmg":
            create_dmg()
    else:
        print("\n" + "="*50)
        print("Build failed!")
        print("="*50)
        sys.exit(1)
