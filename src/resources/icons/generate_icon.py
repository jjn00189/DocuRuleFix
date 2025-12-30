"""Generate application icons for DocuRuleFix

This script creates icons for the application using PIL/Pillow.
"""

from PIL import Image, ImageDraw
import os
import sys
import subprocess
import tempfile
import shutil


def create_icon(size=256):
    """Create a DocuRuleFix icon

    The icon features:
    - A document (Word page) shape
    - A checkmark symbol
    - A gear/wrench symbol for "fix"
    - Blue gradient background

    Args:
        size: Icon size in pixels (square)

    Returns:
        PIL Image object
    """
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    bg_color = (41, 98, 255, 255)  # Blue
    bg_dark = (30, 70, 180, 255)   # Darker blue for gradient effect
    white = (255, 255, 255, 255)
    accent = (100, 180, 255, 255)  # Light blue accent

    # Padding
    pad = size // 16
    doc_width = size // 2
    doc_height = size * 2 // 3

    # Draw document background (rounded rectangle)
    doc_x = (size - doc_width) // 2
    doc_y = (size - doc_height) // 2

    # Draw main document shape
    draw.rounded_rectangle(
        [doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
        radius=size // 32,
        fill=bg_color,
        outline=bg_dark,
        width=size // 64
    )

    # Draw document fold (top-right corner)
    fold_size = size // 8
    fold_points = [
        (doc_x + doc_width - fold_size, doc_y),
        (doc_x + doc_width, doc_y + fold_size),
        (doc_x + doc_width - fold_size, doc_y + fold_size)
    ]
    draw.polygon(fold_points, fill=bg_dark)

    # Draw horizontal lines to represent text
    line_height = size // 24
    line_spacing = size // 12
    start_y = doc_y + fold_size + size // 16

    for i in range(4):
        y = start_y + i * line_spacing
        # Last line shorter to show variety
        line_width = doc_width - size // 4 if i == 3 else doc_width - size // 3
        line_x = doc_x + size // 8
        draw.rectangle(
            [line_x, y, line_x + line_width, y + line_height],
            fill=accent
        )

    # Draw checkmark (symbol for validation)
    check_size = size // 4
    check_x = size // 2 - check_size // 2
    check_y = doc_y + doc_height - size // 3

    # Checkmark circle background
    circle_radius = check_size // 2 + size // 32
    draw.ellipse(
        [check_x - circle_radius, check_y - circle_radius,
         check_x + circle_radius, check_y + circle_radius],
        fill=(34, 197, 94, 255)  # Green for success
    )

    # Draw checkmark
    check_thickness = size // 64
    # Checkmark points
    check_start = (check_x - check_size // 4, check_y)
    check_middle = (check_x, check_y + check_size // 4)
    check_end = (check_x + check_size // 3, check_y - check_size // 6)

    # Draw checkmark as thick lines
    draw.line(
        [check_start, check_middle, check_end],
        fill=white,
        width=check_thickness * 2
    )

    return img


def generate_all_icons():
    """Generate icons in multiple formats and sizes"""
    # Output directory
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate different sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]

    print("Generating icons...")

    # Generate PNG icons
    for size in sizes:
        img = create_icon(size)
        png_path = os.path.join(output_dir, f"icon_{size}x{size}.png")
        img.save(png_path, "PNG")
        print(f"  Created: {png_path}")

    # Generate ICO file (Windows) with multiple sizes
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_img = create_icon(256)
    ico_path = os.path.join(output_dir, "DocuRuleFix.ico")
    ico_img.save(ico_path, format="ICO", sizes=ico_sizes)
    print(f"  Created: {ico_path}")

    # Generate ICNS file (macOS) if on macOS or iconutil is available
    if sys.platform == 'darwin':
        try:
            generate_icns(output_dir)
        except Exception as e:
            print(f"  Warning: Could not generate .icns file: {e}")
            print(f"  Note: .icns files require macOS and iconutil")

    print("\nAll icons generated successfully!")


def generate_icns(output_dir: str):
    """Generate macOS .icns icon file

    This creates an iconset directory and uses iconutil to convert it to .icns

    Args:
        output_dir: Directory to save the .icns file
    """
    icns_path = os.path.join(output_dir, "DocuRuleFix.icns")
    iconset_name = "DocuRuleFix.iconset"

    # Create temporary iconset directory
    with tempfile.TemporaryDirectory() as temp_dir:
        iconset_path = os.path.join(temp_dir, iconset_name)
        os.makedirs(iconset_path)

        # Required sizes for iconset
        iconset_sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),  # 32x32
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),  # 64x64
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),  # 256x256
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),  # 512x512
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),  # 1024x1024
        ]

        # Copy/scale images to iconset
        for size, filename in iconset_sizes:
            # Find the closest available size
            available_sizes = [16, 32, 48, 64, 128, 256, 512]
            closest = min(available_sizes, key=lambda x: abs(x - size))

            # Load the closest size image
            img = create_icon(closest)
            if size != closest:
                img = img.resize((size, size), Image.Resampling.LANCZOS)

            # Save to iconset
            dest_path = os.path.join(iconset_path, filename)
            img.save(dest_path, "PNG")

        # Use iconutil to create .icns
        subprocess.run([
            'iconutil',
            '-c', 'icns',
            '-o', icns_path,
            iconset_path
        ], check=True)

        print(f"  Created: {icns_path}")


if __name__ == "__main__":
    generate_all_icons()
