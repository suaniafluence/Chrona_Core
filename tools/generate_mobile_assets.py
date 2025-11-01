#!/usr/bin/env python3
"""
Generate mobile app assets for Chrona Mobile
Creates icon.png, adaptive-icon.png, splash.png, and favicon.png
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# Chrona brand colors
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_gradient_background(width, height, color1, color2):
    """Create a vertical gradient background"""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            mask_data.append(int(255 * (y / height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_clock_icon(draw, center_x, center_y, radius, color):
    """Draw a stylized clock icon"""
    # Outer circle
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        outline=color,
        width=int(radius * 0.1)
    )

    # Clock hands (showing 10:10 - traditional watch marketing time)
    # Hour hand (10 o'clock) - shorter
    hour_angle = math.radians(300)  # 10 o'clock = 300 degrees
    hour_length = radius * 0.5
    hour_end_x = center_x + hour_length * math.sin(hour_angle)
    hour_end_y = center_y - hour_length * math.cos(hour_angle)
    draw.line(
        [(center_x, center_y), (hour_end_x, hour_end_y)],
        fill=color,
        width=int(radius * 0.08)
    )

    # Minute hand (2 o'clock position) - longer
    minute_angle = math.radians(60)  # 2 o'clock = 60 degrees
    minute_length = radius * 0.7
    minute_end_x = center_x + minute_length * math.sin(minute_angle)
    minute_end_y = center_y - minute_length * math.cos(minute_angle)
    draw.line(
        [(center_x, center_y), (minute_end_x, minute_end_y)],
        fill=color,
        width=int(radius * 0.08)
    )

    # Center dot
    dot_radius = radius * 0.08
    draw.ellipse(
        [center_x - dot_radius, center_y - dot_radius,
         center_x + dot_radius, center_y + dot_radius],
        fill=color
    )

    # Hour markers (12, 3, 6, 9)
    marker_positions = [0, 90, 180, 270]  # 12, 3, 6, 9 o'clock
    marker_outer = radius * 0.85
    marker_inner = radius * 0.7
    for angle_deg in marker_positions:
        angle = math.radians(angle_deg)
        outer_x = center_x + marker_outer * math.sin(angle)
        outer_y = center_y - marker_outer * math.cos(angle)
        inner_x = center_x + marker_inner * math.sin(angle)
        inner_y = center_y - marker_inner * math.cos(angle)
        draw.line(
            [(inner_x, inner_y), (outer_x, outer_y)],
            fill=color,
            width=int(radius * 0.06)
        )

def generate_icon(output_path, size=1024):
    """Generate main app icon (1024x1024)"""
    print(f"Generating icon.png ({size}×{size})...")

    # Create image with gradient background
    img = create_gradient_background(size, size,
                                     hex_to_rgb(PRIMARY_COLOR),
                                     hex_to_rgb(SECONDARY_COLOR))
    draw = ImageDraw.Draw(img)

    # Draw clock icon (70% of size)
    clock_radius = int(size * 0.35)
    center = size // 2
    draw_clock_icon(draw, center, center, clock_radius, (255, 255, 255))

    # Save
    img.save(output_path, 'PNG')
    print(f"[OK] Created {output_path}")

def generate_adaptive_icon(output_path, size=1024):
    """Generate Android adaptive icon (1024x1024)"""
    print(f"Generating adaptive-icon.png ({size}×{size})...")

    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Safe zone is 66% of the square (circle)
    safe_radius = int(size * 0.33)
    center = size // 2

    # Draw colored circle background (safe zone)
    draw.ellipse(
        [center - safe_radius, center - safe_radius,
         center + safe_radius, center + safe_radius],
        fill=hex_to_rgb(PRIMARY_COLOR)
    )

    # Draw clock icon (smaller, within safe zone)
    clock_radius = int(safe_radius * 0.6)
    draw_clock_icon(draw, center, center, clock_radius, (255, 255, 255))

    # Save
    img.save(output_path, 'PNG')
    print(f"[OK] Created {output_path}")

def generate_splash(output_path, width=1242, height=2436):
    """Generate splash screen (1242x2436)"""
    print(f"Generating splash.png ({width}×{height})...")

    # Create gradient background
    img = create_gradient_background(width, height,
                                     hex_to_rgb(PRIMARY_COLOR),
                                     hex_to_rgb(SECONDARY_COLOR))
    draw = ImageDraw.Draw(img)

    # Draw clock icon (30% of height)
    clock_radius = int(height * 0.15)
    center_x = width // 2
    center_y = height // 2
    draw_clock_icon(draw, center_x, center_y, clock_radius, (255, 255, 255))

    # Try to add "CHRONA" text below the clock
    try:
        # Try to use a default font, fall back to basic if not available
        font_size = int(height * 0.04)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "CHRONA"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = center_x - text_width // 2
        text_y = center_y + clock_radius + int(height * 0.05)

        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"  Warning: Could not add text: {e}")

    # Save
    img.save(output_path, 'PNG')
    print(f"[OK] Created {output_path}")

def generate_favicon(output_path, size=48):
    """Generate favicon (48x48)"""
    print(f"Generating favicon.png ({size}×{size})...")

    # Create small icon with solid background
    img = Image.new('RGB', (size, size), hex_to_rgb(PRIMARY_COLOR))
    draw = ImageDraw.Draw(img)

    # Draw simplified clock icon
    clock_radius = int(size * 0.35)
    center = size // 2
    draw_clock_icon(draw, center, center, clock_radius, (255, 255, 255))

    # Save
    img.save(output_path, 'PNG')
    print(f"[OK] Created {output_path}")

def main():
    """Generate all mobile assets"""
    print("Generating Chrona Mobile Assets\n")

    # Determine assets directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(project_root, 'apps', 'mobile', 'assets')

    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)

    # Generate all assets
    generate_icon(os.path.join(assets_dir, 'icon.png'), 1024)
    generate_adaptive_icon(os.path.join(assets_dir, 'adaptive-icon.png'), 1024)
    generate_splash(os.path.join(assets_dir, 'splash.png'), 1242, 2436)
    generate_favicon(os.path.join(assets_dir, 'favicon.png'), 48)

    print("\nAll assets generated successfully!")
    print(f"Location: {assets_dir}")
    print("\nChecklist:")
    print("  [OK] icon.png (1024x1024)")
    print("  [OK] adaptive-icon.png (1024x1024)")
    print("  [OK] splash.png (1242x2436)")
    print("  [OK] favicon.png (48x48)")
    print("\nNote: These are placeholder assets. Replace with professional designs later.")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("ERROR: Pillow (PIL) is not installed.")
        print("Install it with: pip install Pillow")
        exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
