import base64
import io
import anthropic
from PIL import Image, ImageDraw
import string

GRID_SIZE = 50
PADDING_TOP = 100
PADDING_LEFT = 100

def add_padding_to_image(image, padding_top=PADDING_TOP, padding_left=PADDING_LEFT):
    width, height = 1000, 1000
    new_width = width + padding_left
    new_height = height + padding_top
    # Create a new white image with padding
    padded_image = Image.new('RGB', (new_width, new_height), color='white')
    padded_image.paste(image, (padding_left, padding_top))
    
    return padded_image, width // GRID_SIZE, height // GRID_SIZE

class Claude:
    #client: Claude
    #api_key: string

    def __init__(self,api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic()
        self.history = []
        

    def image_to_text(self, image, media_type, model):
        print("Augmenting image with grid")

        # Add padding to the image and get dimensions

        img_with_padding, cols, rows = add_padding_to_image(image)

        # Convert the image to base64
        buffered = io.BytesIO()
        img_with_padding.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print("Sending request to Anthropic")
        self.history.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_base64,
                    },
                },
                {
                    "type": "text",
                    "text": f"Describe this image (make sure to be as descriptive as possible and compare it to the previous image) in details and analyze this image as if it had a chess-like grid overlay with {cols} columns (A-{string.ascii_uppercase[cols-1]}) and {rows} rows (1-{rows}). Each grid cell is {GRID_SIZE}x{GRID_SIZE} pixels. Identify all interesting or notable elements in the image. For each element, provide its location using the grid coordinates (e.g., ['B2', 'B3'] for an element spanning two cells) and a brief description. Format your response as a JSON object with an 'elements' array, where each element has 'grid_locations' (an array of grid coordinates) and 'description' fields (also be as descriptive as possible). Also a 'overall' field that describes the entire image. Limit your response to the 20 most interesting or notable elements."
                }
            ]
        })

        response = self.client.messages.create(
            model = model, #claude-3-5-sonnet-20241022
            max_tokens=2048,
            messages=self.history,
        )
        print("Request received!")
        
         # Add model's response to the conversation history
        self.history.append({
            "role": "assistant",
            "content": response.content[0].text
        })
        
        return response
