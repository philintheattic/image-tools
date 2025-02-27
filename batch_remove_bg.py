import sys
import os
from rembg import remove
from PIL import Image
import pillow_heif  # HEIC support
from multiprocessing import Pool, cpu_count
from tqdm import tqdm  # Progress bar goodness

def remove_bg(image_path):
    """Removes background from a single image and saves it with _sticker suffix."""
    try:
        dir_name, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)

        # Convert HEIC to PNG if necessary
        if ext.lower() == ".heic":
            heif_image = pillow_heif.open_heif(image_path)
            image = Image.frombytes(heif_image.mode, heif_image.size, heif_image.data)
        else:
            image = Image.open(image_path)

        # Remove background
        output = remove(image)

        # Define output filename
        output_path = os.path.join(dir_name, f"{name}_sticker.png")

        # Save as transparent PNG
        output.save(output_path)

        return f"✅ Processed: {file_name} → {name}_sticker.png"
    
    except Exception as e:
        return f"❌ Error processing {image_path}: {e}"

def process_images(image_paths):
    """Handles multiprocessing with a progress bar."""
    num_workers = max(1, cpu_count() // 2)  # Use half the CPU cores
    print(f"⚡ Using {num_workers} parallel workers...")

    with Pool(num_workers) as pool:
        # Wrap pool.imap with tqdm for progress tracking
        for result in tqdm(pool.imap(remove_bg, image_paths), total=len(image_paths), desc="Processing"):
            print(result)  # Print status for each image

    print("🎉 Batch processing completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_paths = [path for path in sys.argv[1:] if os.path.isfile(path)]

        if image_paths:
            process_images(image_paths)
        else:
            print("⚠️ No valid image files found.")
    else:
        print("🚨 Drag and drop images onto this script to process them.")
