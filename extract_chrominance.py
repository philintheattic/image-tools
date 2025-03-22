import cv2
import os
import argparse
import numpy as np
from pathlib import Path

def extract_chrominance_with_alpha(input_path, output_path=None, y_value=128, alpha_mode=False, alpha_value=255):
    """
    Extract only the Cb and Cr chrominance channels from an image,
    with options to set the Y channel to a specific value or make it transparent.
    
    Args:
        input_path (str): Path to the input image
        output_path (str, optional): Path to save the output image. If None,
                                    will use input_path + '_chroma.png'
        y_value (int): Value to set the Y channel to (0-255), default is 128 (middle gray)
        alpha_mode (bool): If True, adds transparency based on the Y channel
        alpha_value (int): Base alpha value for transparency (0-255), only used if alpha_mode is True
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate values
    y_value = max(0, min(255, int(y_value)))
    alpha_value = max(0, min(255, int(alpha_value)))
    
    # Read the image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Error: Could not read image from {input_path}")
        return False
    
    # Check if the image already has an alpha channel
    has_alpha = img.shape[2] == 4 if len(img.shape) == 3 else False
    
    # Convert BGR to YCrCb
    if has_alpha:
        # Preserve the alpha channel
        alpha = img[:, :, 3]
        bgr = img[:, :, :3]
        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    else:
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    
    # Get Y channel for potential alpha calculation
    y_original = ycrcb[:, :, 0].copy() if alpha_mode else None
    
    # Set Y channel to the specified value
    ycrcb[:, :, 0] = y_value
    
    # Convert back to BGR
    bgr_result = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    
    # Handle alpha channel
    if alpha_mode:
        # Create BGRA image
        bgra = np.zeros((bgr_result.shape[0], bgr_result.shape[1], 4), dtype=np.uint8)
        bgra[:, :, :3] = bgr_result
        
        # Set alpha based on original Y value
        if alpha_value == 255:
            # Simple transparency: Y becomes alpha
            bgra[:, :, 3] = y_original
        else:
            # Scaled transparency: adjust based on the specified alpha_value
            # This scales the Y values to maintain their relative relationship
            # but caps the maximum transparency at alpha_value
            scale_factor = alpha_value / 255.0
            bgra[:, :, 3] = (y_original * scale_factor).astype(np.uint8)
        
        result_img = bgra
        
        # Make sure output is PNG to preserve transparency
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_chroma_alpha.png"
        else:
            # Ensure output has PNG extension
            base, ext = os.path.splitext(output_path)
            if ext.lower() != '.png':
                output_path = f"{base}.png"
                print(f"Note: Output format changed to PNG to preserve transparency")
    else:
        # No transparency, use regular BGR output
        result_img = bgr_result
        
        # Create default output path if none specified
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_chroma_y{y_value}{ext}"
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the result
    success = cv2.imwrite(output_path, result_img)
    if success:
        print(f"Processed: {input_path} -> {output_path}")
        if alpha_mode:
            print(f"  Transparency applied based on original Y channel")
        else:
            print(f"  Y set to {y_value}")
        return True
    else:
        print(f"Error: Failed to save image to {output_path}")
        return False

def batch_process_folder(input_folder, output_folder=None, y_value=128, alpha_mode=False, alpha_value=255):
    """
    Process all images in a folder.
    
    Args:
        input_folder (str): Path to the folder containing images
        output_folder (str, optional): Path to save the output images
        y_value (int): Value to set the Y channel to (0-255), default is 128
        alpha_mode (bool): If True, adds transparency based on the Y channel
        alpha_value (int): Base alpha value for transparency (0-255)
    
    Returns:
        tuple: (count_success, count_fail) Number of successfully processed and failed images
    """
    input_folder = Path(input_folder)
    
    if not input_folder.exists() or not input_folder.is_dir():
        print(f"Error: {input_folder} is not a valid directory")
        return 0, 0
    
    # Setup output folder
    folder_suffix = "_alpha" if alpha_mode else f"_y{y_value}"
    if output_folder is None:
        output_folder = input_folder / f"chrominance{folder_suffix}"
    else:
        output_folder = Path(output_folder)
    
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
    
    # Image file extensions to process
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    
    count_success = 0
    count_fail = 0
    
    if alpha_mode:
        print(f"Processing images in {input_folder} with transparency...")
    else:
        print(f"Processing images in {input_folder} with Y={y_value}...")
    
    # Find all image files in the input folder
    for img_path in input_folder.iterdir():
        if img_path.is_file() and img_path.suffix.lower() in image_extensions:
            output_filename = f"{img_path.stem}_alpha.png" if alpha_mode else f"{img_path.stem}_y{y_value}{img_path.suffix}"
            
            # For alpha mode, always use PNG for output
            if alpha_mode:
                output_path = output_folder / f"{img_path.stem}_alpha.png"
            else:
                output_path = output_folder / output_filename
            
            if extract_chrominance_with_alpha(str(img_path), str(output_path), y_value, alpha_mode, alpha_value):
                count_success += 1
            else:
                count_fail += 1
    
    print(f"\nBatch processing complete.")
    print(f"Successfully processed: {count_success} images")
    if count_fail > 0:
        print(f"Failed to process: {count_fail} images")
    
    return count_success, count_fail

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract chrominance channels from images with transparency options")
    
    # Create mutually exclusive group for input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-i", "--input", help="Path to the input image file")
    input_group.add_argument("-f", "--folder", help="Path to the folder containing images to process")
    
    # Output options
    parser.add_argument("-o", "--output", help="Path to save the output image or folder", default=None)
    
    # Processing mode group (mutual exclusivity between Y-value and Alpha mode)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-y", "--y_value", type=int, default=128, 
                        help="Value to set the Y channel to (0-255, default=128)")
    mode_group.add_argument("-a", "--alpha", action="store_true",
                        help="Create a transparent version with alpha channel based on Y values")
    
    # Alpha intensity
    parser.add_argument("--alpha_value", type=int, default=255,
                        help="Maximum alpha value (0-255, default=255)")
    
    args = parser.parse_args()
    
    # Set alpha mode flag based on arguments
    alpha_mode = args.alpha
    
    if args.input:
        # Process a single image
        extract_chrominance_with_alpha(args.input, args.output, args.y_value, alpha_mode, args.alpha_value)
    elif args.folder:
        # Process a folder of images
        batch_process_folder(args.folder, args.output, args.y_value, alpha_mode, args.alpha_value)