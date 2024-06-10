import requests
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from transformers import BitsAndBytesConfig
import json


double_quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True)
app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
@app.get("/")
async def root():
    return {"message": "Welcome to Image Translation."}

model_id = "llava-hf/llava-1.5-7b-hf"

# Load the model and processor
model = LlavaForConditionalGeneration.from_pretrained(
    model_id,
    quantization_config=double_quant_config
)
processor = AutoProcessor.from_pretrained(model_id)

class ImagePrompt(BaseModel):
    url: str
    prompt: str

@app.post("/process_image")
async def process_image(image_prompt: ImagePrompt):
    try:
        # Load the image
        raw_image = Image.open(requests.get(image_prompt.url, stream=True).raw)

        # Prepare the inputs
        prompt = f"USER: <image>\n{image_prompt.prompt}\nASSISTANT:"
        inputs = processor(prompt, raw_image, return_tensors='pt').to(device)

        # Generate the output
        output = model.generate(**inputs, max_new_tokens=200, do_sample=False)

        # Decode the response
        response = processor.decode(output[0][2:], skip_special_tokens=True)

        # Save the response to a JSON file
        response_data = {
            "url": image_prompt.url,
            "prompt": image_prompt.prompt,
            "response": response,
        }
        with open("response.json", "a") as f:
            json.dump(response_data, f)
            f.write("\n")

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



