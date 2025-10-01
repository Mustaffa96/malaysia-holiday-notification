#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate a simple icon for the Malaysia Holiday Notifier application.
This creates both PNG and ICO files with the Malaysian flag colors and a 14-point star,
accurately representing elements of the Malaysian flag.
"""

import os
import math

from PIL import Image, ImageDraw


def create_icon(output_png_path="icon.png", output_ico_path="icon.ico", size=128):
    """
    Create a simple icon with Malaysian flag colors.

    Args:
        output_path (str): Path to save the icon
        size (int): Size of the icon in pixels
    """
    # Create a new image with white background
    img = Image.new('RGBA', (size, size), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Malaysian flag colors
    blue = (0, 0, 128, 255)  # Dark blue
    red = (206, 17, 38, 255)  # Red

    # Draw alternating stripes (Malaysian flag has 14 stripes)
    stripe_height = size // 14
    white = (255, 255, 255, 255)
    for i in range(14):
        color = red if i % 2 == 0 else white
        draw.rectangle([(0, i * stripe_height), (size, (i + 1) * stripe_height)], fill=color)

    # Draw blue rectangle in top left (canton)
    canton_width = size // 2
    canton_height = size // 2
    draw.rectangle([(0, 0), (canton_width, canton_height)], fill=blue)

    # Draw a 14-point star in the blue canton
    # Calculate star points
    star_center_x = canton_width // 2
    star_center_y = canton_height // 2
    outer_radius = canton_width // 3
    inner_radius = outer_radius // 2
    num_points = 14
    
    star_points = []
    for i in range(num_points * 2):
        # Alternate between outer and inner points
        radius = outer_radius if i % 2 == 0 else inner_radius
        # Calculate angle (in radians)
        angle = (i * 2 * 3.14159) / (num_points * 2)
        
        x = star_center_x + int(radius * math.cos(angle))
        y = star_center_y + int(radius * math.sin(angle))
        star_points.append((x, y))
    
    # Draw the star
    draw.polygon(star_points, fill=(255, 255, 0, 255))

    # Draw a calendar icon in the bottom right
    calendar_size = size // 3
    calendar_x = size - calendar_size - size // 10
    calendar_y = size - calendar_size - size // 10

    # Calendar background
    draw.rectangle(
        [(calendar_x, calendar_y),
         (calendar_x + calendar_size, calendar_y + calendar_size)],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=size//50
    )

    # Calendar top bar
    draw.rectangle(
        [(calendar_x, calendar_y),
         (calendar_x + calendar_size, calendar_y + calendar_size//5)],
        fill=red,
        outline=(0, 0, 0, 255),
        width=size//50
    )

    # Calendar lines
    line_spacing = calendar_size // 4
    for i in range(1, 3):
        y = calendar_y + calendar_size//5 + i * line_spacing
        draw.line(
            [(calendar_x + calendar_size//10, y),
             (calendar_x + calendar_size - calendar_size//10, y)],
            fill=(0, 0, 0, 255),
            width=size//100
        )

    # Save as PNG
    img.save(output_png_path)
    print(f"PNG icon created at {output_png_path}")
    
    # Save as ICO
    try:
        # ICO format requires sizes to be powers of 2
        ico_sizes = [16, 32, 48, 64, 128, 256]
        ico_images = []
        
        # Create versions at different sizes for the ICO file
        for ico_size in ico_sizes:
            if ico_size <= size:  # Only include sizes up to the original size
                resized_img = img.resize((ico_size, ico_size), Image.LANCZOS)
                ico_images.append(resized_img)
        
        # Save as ICO with multiple sizes
        img.save(output_ico_path, format='ICO', sizes=[(i.width, i.height) for i in ico_images])
        print(f"ICO icon created at {output_ico_path}")
    except Exception as e:
        print(f"Error creating ICO file: {e}")
        print("Continuing with PNG only...")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(script_dir, "icon.png")
    ico_path = os.path.join(script_dir, "icon.ico")
    create_icon(png_path, ico_path)
    print("To use these icons, make sure you have Pillow installed:")
    print("pip install Pillow")
