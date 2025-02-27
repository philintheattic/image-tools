import sys
import os
from rembg import remove
from PIL import Image
from pillow_heif import register_heif_opener


def remove_bg(image_path):
    # include support for .HEIC files
    register_heif_opener()

    # Get the directory and filename
    dir_name, file_name = os.path.split(image_path)
    name, ext = os.path.splitext(file_name)

    # Open the image
    image = Image.open(image_path)

    # Remove background
    output = remove(image)

    # Define output filename
    output_path = os.path.join(dir_name, f"{name}_sticker.png")

    # Save as transparent PNG
    output.save(output_path)

    print(f"✅ Background removed! Saved as: {output_path}")
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process all dropped files
        for image_path in sys.argv[1:]:
            if os.path.isfile(image_path):  # Ensure it's a file
                remove_bg(image_path)
            else:
                print(f"⚠️ Skipping: {image_path} (not a valid file)")
    else:
        print("🚨 Drag and drop images onto this script to process them.")

