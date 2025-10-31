#!/usr/bin/env python3
"""
Extract individual sprites and portraits from NPC sprite sheets.

Sheet structure:
- 160x160 pixels total
- 5 rows x 5 columns
- Each cell is 32x32 pixels
- First column: 16x16 pixel sprites in groups of 4 (arranged 2x2 within each 32x32 cell)
- Remaining columns: 32x32 pixel portraits

Character naming:
- Create a text file with the same name as your sprite sheet (e.g., npc-sprites-page-1.txt)
- Add one character name per line (20 names total, one for each row+sprite combination)
- Names are assigned to sprites in order: row0 sprites 1-4, row1 sprites 1-4, etc.
"""

from PIL import Image
import os
import sys
import subprocess
import shutil


def load_character_names(sheet_path):
    """
    Load character names from a text file corresponding to the sprite sheet.

    Args:
        sheet_path: Path to the sprite sheet image

    Returns:
        List of character names (20 names expected), or None if file doesn't exist
    """
    base_name = os.path.splitext(sheet_path)[0]
    names_file = f"{base_name}.txt"

    if not os.path.exists(names_file):
        return None

    with open(names_file, 'r') as f:
        names = [line.strip() for line in f if line.strip()]

    if len(names) != 20:
        print(f"Warning: Expected 20 names in {names_file}, found {len(names)}")
        print("Names should be provided for all 20 characters (5 rows × 4 sprites)")

    return names


def sanitize_filename(name):
    """
    Sanitize a character name to be safe for use in filenames.

    Args:
        name: Character name to sanitize

    Returns:
        Safe filename string
    """
    # Replace spaces and special characters with underscores
    safe_name = name.replace(' ', '_')
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-'))
    return safe_name


def check_optipng_available():
    """
    Check if optipng is available on the system.

    Returns:
        bool: True if optipng is available, False otherwise
    """
    return shutil.which('optipng') is not None


def optimize_png_with_optipng(file_path):
    """
    Optimize a PNG file using optipng.

    Args:
        file_path: Path to the PNG file to optimize
    """
    try:
        # Use -o2 for good compression without being too slow
        # -quiet to suppress output
        subprocess.run(
            ['optipng', '-o2', '-quiet', file_path],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        # If optipng fails, just continue - the file is already saved
        pass


def extract_sprites_from_sheet(sheet_path, output_dir, use_optipng=False):
    """
    Extract all sprites and portraits from a sprite sheet.

    Args:
        sheet_path: Path to the sprite sheet image
        output_dir: Directory to save extracted images
        use_optipng: Whether to use optipng for additional optimization
    """
    # Load the sprite sheet
    sheet = Image.open(sheet_path)

    # Verify dimensions
    if sheet.size != (160, 160):
        print(f"Warning: Expected 160x160 pixels, got {sheet.size}")

    # Get base name for output files
    base_name = os.path.splitext(os.path.basename(sheet_path))[0]

    # Load character names if available
    character_names = load_character_names(sheet_path)
    if character_names:
        print(f"Loaded {len(character_names)} character names from {base_name}.txt")
    else:
        print(f"No character names file found ({base_name}.txt)")
        print("Using default naming (row/sprite numbers)")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Track files for batch optipng optimization
    files_to_optimize = []

    # Extract sprites from first column (16x16 sprites)
    print(f"Processing {sheet_path}...")
    print("Extracting 16x16 sprites from first column...")

    character_index = 0

    for row in range(5):  # 5 rows
        # Each 32x32 cell contains 4 sprites in a 2x2 arrangement
        base_y = row * 32
        base_x = 0  # First column

        # Extract the 4 sprites from this cell
        sprite_positions = [
            (0, 0, "1"),   # Top-left
            (16, 0, "2"),  # Top-right
            (0, 16, "3"),  # Bottom-left
            (16, 16, "4")  # Bottom-right
        ]

        for offset_x, offset_y, sprite_num in sprite_positions:
            # Calculate absolute position
            x = base_x + offset_x
            y = base_y + offset_y

            # Extract 16x16 sprite
            sprite = sheet.crop((x, y, x + 16, y + 16))

            # Determine filename
            if character_names and character_index < len(character_names):
                char_name = sanitize_filename(character_names[character_index])
                sprite_name = f"{char_name}face.png"
            else:
                sprite_name = f"{base_name}_row{row}_sprite{sprite_num}.png"

            sprite_path = os.path.join(output_dir, sprite_name)
            # Save with optimization: optimize=True for smaller file size
            sprite.save(sprite_path, optimize=True)
            print(f"  Saved: {sprite_name}")

            # Track for optipng optimization
            if use_optipng:
                files_to_optimize.append(sprite_path)

            character_index += 1

    # Extract portraits from remaining columns (32x32 portraits)
    print("Extracting 32x32 portraits from remaining columns...")

    character_index = 0

    for row in range(5):  # 5 rows
        for col in range(1, 5):  # Columns 1-4 (skip column 0 which has sprites)
            # Calculate position
            x = col * 32
            y = row * 32

            # Extract 32x32 portrait
            portrait = sheet.crop((x, y, x + 32, y + 32))

            # Calculate which sprite this portrait corresponds to
            # Each row has 4 sprites, and 4 portraits (one per column)
            sprite_index = (col - 1) + 1  # portraits 1-4 for sprites 1-4

            # Determine filename
            if character_names and character_index < len(character_names):
                char_name = sanitize_filename(character_names[character_index])
                portrait_name = f"{char_name}.png"
            else:
                portrait_name = f"{base_name}_row{row}_sprite{sprite_index}_portrait.png"

            portrait_path = os.path.join(output_dir, portrait_name)
            # Save with optimization: optimize=True for smaller file size
            portrait.save(portrait_path, optimize=True)
            print(f"  Saved: {portrait_name}")

            # Track for optipng optimization
            if use_optipng:
                files_to_optimize.append(portrait_path)

            character_index += 1

    # Run optipng optimization if requested
    if use_optipng and files_to_optimize:
        print(f"Optimizing {len(files_to_optimize)} files with optipng...")
        for file_path in files_to_optimize:
            optimize_png_with_optipng(file_path)
        print("Optimization complete!")

    print(f"Extraction complete for {sheet_path}!")


def main():
    """Main function to process all sprite sheets in the current directory."""
    # Default output directory
    output_dir = "extracted_sprites"

    # Find all sprite sheet files
    sprite_sheets = [f for f in os.listdir(".") if f.startswith("npc-sprites-") and
                     (f.endswith(".png") or f.endswith(".webp") or f.endswith(".jpg"))]

    if not sprite_sheets:
        print("No sprite sheets found matching pattern 'npc-sprites-*'")
        print("Usage: python extract_sprites.py [output_directory]")
        return

    # Allow custom output directory
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    # Check if optipng is available
    use_optipng = check_optipng_available()
    if use_optipng:
        print("✓ optipng detected - will use for additional optimization")
    else:
        print("⚠ optipng not found - using basic PNG optimization only")
        print("  Install optipng for better compression:")
        print("    macOS:   brew install optipng")
        print("    Linux:   apt-get install optipng  (or yum/pacman)")
        print("    Windows: choco install optipng  (or download from http://optipng.sourceforge.net/)")

    print(f"Found {len(sprite_sheets)} sprite sheet(s)")
    print(f"Output directory: {output_dir}\n")

    # Process each sheet
    for sheet_path in sorted(sprite_sheets):
        extract_sprites_from_sheet(sheet_path, output_dir, use_optipng)
        print()

    print(f"All done! Extracted sprites saved to '{output_dir}/' directory")


if __name__ == "__main__":
    main()
