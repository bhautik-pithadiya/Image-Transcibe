import requests
from PIL import Image
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from transformers import BitsAndBytesConfig
import json
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


double_quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True)    
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_id = "llava-hf/llava-1.5-7b-hf"

# Load the model and processor
model = LlavaForConditionalGeneration.from_pretrained(
    model_id,
    quantization_config=double_quant_config
)
processor = AutoProcessor.from_pretrained(model_id)
logger.info(f"Model Loaded")

class ImagePrompt(BaseModel):
    url: str
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_image")
async def process_image(imageLink: str = Form(...), prompt: str = Form(...), username: str = Form(...)):
    logger.info(f"Received form data - ImageLink: {imageLink}, Prompt: {prompt}, Username: {username}")
    try:
        logger.info(f"Received form data - ImageLink: {imageLink}, Prompt: {prompt}, Username: {username}")
        # Load the image
        # print(username,imageLink)
        list_of_images = imageLink.split(' ')
        if len(list_of_images)>1:
            output = []
            i=0
            for images in list_of_images:
                raw_image = Image.open(requests.get(images, stream=True).raw)

                # Prepare the inputs
                formatted_prompt = f"USER: <image>\n{prompt}\nASSISTANT:"
                inputs = processor(formatted_prompt, raw_image, return_tensors='pt').to(device)

                # Generate the output
                start_time = datetime.now()
                output.append(model.generate(**inputs, max_new_tokens=200, do_sample=False))
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                # Decode the response
                response = processor.decode(output[i][0][2:], skip_special_tokens=True)
                i+=1
                # Save the response to a JSON file
                response_data = {
                    "url": imageLink,
                    "prompt": prompt,
                    "response": response,
                    "username": username,
                    "processing_time":processing_time
                }
                with open("response.json", "a") as f:
                    json.dump(response_data, f)
                    f.write("\n")

            return {"response": response}
        else:
            raw_image = Image.open(requests.get(imageLink, stream=True).raw)

            # Prepare the inputs
            formatted_prompt = f"USER: <image>\n{prompt}\nASSISTANT:"
            inputs = processor(formatted_prompt, raw_image, return_tensors='pt').to(device)

            # Generate the output
            start_time = datetime.now()
            output = model.generate(**inputs, max_new_tokens=200, do_sample=False)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            # Decode the response
            response = processor.decode(output[0][2:], skip_special_tokens=True)

            # Save the response to a JSON file
            response_data = {
                "url": imageLink,
                "prompt": prompt,
                "response": response,
                "username": username,
                "processing_time":str(processing_time)                
            }
            with open("response.json", "a") as f:
                json.dump(response_data, f)
                f.write("\n")

            return {"response": response_data['response'],"processing_time":processing_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


