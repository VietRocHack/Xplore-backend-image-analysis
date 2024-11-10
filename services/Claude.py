import anthropic


class Claude:
    #client: Claude
    #api_key: string

    def __init__(self,api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic()
        self.history = []
        

    def image_to_text(self, image, media_type, model):
        self.history.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image in detail. If there is a picture sent before this, point out the difference or progress that has made to get the new picture. If not, ignore this prompt and write about it in response"
                }
            ]
        })
        response = self.client.messages.create(
            model = model, #claude-3-5-sonnet-20241022
            max_tokens=1024,
            messages=self.history,
        )
        
         # Add model's response to the conversation history
        self.history.append({
            "role": "assistant",
            "content": response.content[0].text
        })
        
        print(response.content[0].text)
        return response
