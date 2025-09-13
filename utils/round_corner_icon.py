#!/usr/bin/env python3
"""
Script to convert ICO images to rounded corners and save as ICO format.
"""

import os
import sys
from PIL import Image, ImageDraw


def create_rounded_corners_mask(size, radius):
    """Create a mask for rounded corners"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    return mask


def convert_ico_to_rounded_ico(ico_path, output_path=None, radius_ratio=0.2):
    """
    Convert ICO image to ICO with rounded corners.
    
    Args:
        ico_path (str): Path to the input ICO file
        output_path (str, optional): Path for the output ICO file. 
                                    If None, saves as <original_name>_rounded.ico
        radius_ratio (float): Ratio of corner radius to image size (0-0.5)
    """
    try:
        # Open the ICO file
        img = Image.open(ico_path)
        
        # If ICO has multiple sizes, get the largest one
        if hasattr(img, 'n_frames') and img.n_frames > 1:
            sizes = img.info.get('sizes', [])
            if sizes:
                # Get the largest size
                max_size = max(sizes, key=lambda s: s[0] * s[1])
                img = Image.open(ico_path)
                img.load()
                img = img.resize(max_size, Image.LANCZOS)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create mask for rounded corners
        size = img.size
        radius = int(min(size) * radius_ratio)
        mask = create_rounded_corners_mask(size, radius)
        
        # Apply mask to image
        img.putalpha(mask)
        
        # Determine output path
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(ico_path))[0]
            output_path = os.path.join(
                os.path.dirname(ico_path), 
                f"{base_name}_rounded.ico"
            )
        
        # Save the result as ICO
        img.save(output_path, 'ICO')
        print(f"Successfully saved rounded icon to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python round_corner_icon.py <ico_file> [output_file] [radius_ratio]")
        print("  ico_file: Path to the input ICO file")
        print("  output_file: (Optional) Path for the output ICO file")
        print("  radius_ratio: (Optional) Corner radius ratio (0-0.5), default is 0.2")
        sys.exit(1)
    
    ico_path = sys.argv[1]
    
    if not os.path.exists(ico_path):
        print(f"Error: File '{ico_path}' not found.")
        sys.exit(1)
    
    # Check if file is ICO format
    if not ico_path.lower().endswith('.ico'):
        print("Warning: Input file doesn't have .ico extension.")
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    radius_ratio = 0.2
    if len(sys.argv) > 3:
        try:
            radius_ratio = float(sys.argv[3])
            if not 0 <= radius_ratio <= 0.5:
                raise ValueError("Radius ratio must be between 0 and 0.5")
        except ValueError as e:
            print(f"Error: Invalid radius ratio - {e}")
            sys.exit(1)
    
    result = convert_ico_to_rounded_ico(ico_path, output_path, radius_ratio)
    if result:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()