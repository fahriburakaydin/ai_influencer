import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Set device to CPU explicitly
device = torch.device("cpu")

# Load the processor and the model (BLIP base captioner)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

def generate_visual_caption(image_path: str) -> str:
    """
    Generate a visual caption for the provided image using BLIP.
    
    :param image_path: The path to the image file.
    :return: A visual caption describing the image's content.
    """
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt").to(device)
        out_ids = model.generate(**inputs, max_length=50, num_beams=5)
        caption = processor.decode(out_ids[0], skip_special_tokens=True).strip()
        return caption
    except Exception as e:
        # You could log the error here
        return "Unable to generate caption."

# For testing purposes:
if __name__ == "__main__":
    test_image_path = r"C:\Users\fahri\github\personal\ai_influencer\static\uploads\IMG_20240317_113854-EDIT_1.jpg"
    visual_caption = generate_visual_caption(test_image_path)
    print(visual_caption)




