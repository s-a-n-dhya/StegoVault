import stepic
from PIL import Image
import base64

def hide_data_in_image(image_path, binary_data, output_path):
    # Open the image
    img = Image.open(image_path)

    # Ensure it's in a supported mode (RGB/RGBA/CMYK)
    if img.mode not in ["RGB", "RGBA", "CMYK"]:
        img = img.convert("RGB")

    # Encode the binary data using base64 and convert to bytes
    encoded_data = base64.b64encode(binary_data)

    # Stepic expects bytes, not string, so we decode base64 and pass as-is
    steg_img = stepic.encode(img, encoded_data)

    # Save the resulting image
    steg_img.save(output_path, 'PNG')


def extract_data_from_image(image_path):
    img = Image.open(image_path)

    # Stepic returns bytes — base64 decode it
    hidden_data = stepic.decode(img)

    # Convert back from base64 to original binary
    return base64.b64decode(hidden_data)
