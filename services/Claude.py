import base64
import io
import anthropic
from PIL import Image, ImageDraw, ImageFont
import string

GRID_SIZE = 50
PADDING_TOP = 100
PADDING_LEFT = 100

def add_padded_chess_grid(image, padding_top=PADDING_TOP, padding_left=PADDING_LEFT):
    width, height = image.size
    new_width = width + padding_left
    new_height = height + padding_top
    
    # Create a new white image with padding
    padded_image = Image.new('RGB', (new_width, new_height), color='white')
    padded_image.paste(image, (padding_left, padding_top))
    
    draw = ImageDraw.Draw(padded_image)
    
    # Try to load a larger font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    cols = width // GRID_SIZE
    rows = height // GRID_SIZE

    # Draw vertical lines and label them
    for i in range(cols + 1):
        x = i * GRID_SIZE + padding_left
        draw.line([(x, padding_top), (x, new_height)], fill='red', width=2)
        if i < cols:
            label = string.ascii_uppercase[i]
            draw.text((x + GRID_SIZE//2, padding_top//2), label, fill='red', font=font, anchor="mm")

    # Draw horizontal lines and label them
    for i in range(rows + 1):
        y = i * GRID_SIZE + padding_top
        draw.line([(padding_left, y), (new_width, y)], fill='red', width=2)
        if i < rows:
            label = str(i + 1)
            draw.text((padding_left//2, y + GRID_SIZE//2), label, fill='red', font=font, anchor="mm")

    return padded_image, cols, rows

class Claude:
    #client: Claude
    #api_key: string

    def __init__(self,api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic()
        self.history = []
        

    def image_to_text(self, image, media_type, model, prompt):
        print("Augmenting image with grid")

        # Add padding to the image and get dimensions

        img_with_padding, cols, rows = add_padded_chess_grid(image)

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
                    "text": f"Given the user ask this question: {prompt}. Describe this image (make sure to be as descriptive as possible and compare it to the previous image) in details and analyze this image as if it had a chess-like grid overlay with {cols} columns (A-{string.ascii_uppercase[cols-1]}) and {rows} rows (1-{rows}). Each grid cell is {GRID_SIZE}x{GRID_SIZE} pixels. Identify all interesting or notable elements in the image. For each element, provide its location using the grid coordinates (e.g., ['B2', 'B3'] for an element spanning two cells) and a brief description. Format your response as a JSON object with an 'elements' array, where each element has 'grid_locations' (an array of grid coordinates) and 'description' fields (also be as descriptive as possible). Also a 'overall' field that describes the entire image. Limit your response to the 20 most interesting or notable elements."
                }
            ]
        })
        
        print(self.history)
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
