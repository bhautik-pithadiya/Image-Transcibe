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
from datetime import datetime
import logging
import asyncio
import aiohttp
import uuid
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

model_path = 'model/config.json'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model and processor
with open(model_path,'r') as file:
    config = json.load(file)

print(config['_name_or_path'])

model = LlavaForConditionalGeneration.from_pretrained(
    pretrained_model_name_or_path=config["_name_or_path"],
    config=config  
)
processor = AutoProcessor.from_pretrained(model_path)
logger.info("Model Loaded")

def transform_list_of_dicts(data):
    transformed_dict = {}
    
    for entry in data:
        for key, value in entry.items():
            if key not in transformed_dict:
                transformed_dict[key] = []
            transformed_dict[key].append(value)
    
    return transformed_dict

class ImagePrompt(BaseModel):
    url: str
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_image")
async def process_image(imageLink: str = Form(...), prompt: str = Form(...), username: str = Form(...)):
    try:
        logger.info(f"Received form data - ImageLink: {imageLink}, Prompt: {prompt}, Username: {username}")

        # Handle multiple image links
        list_of_images = imageLink.split(' ')
        if len(list_of_images) > 1:
            tasks = [process_single_image(image, prompt, username) for image in list_of_images]
            start_time = datetime.now()
            results = await asyncio.gather(*tasks)
            response_data = transform_list_of_dicts(results)
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            response_data["total_processing_time"] = str(total_processing_time)
        else:
            start_time = datetime.now()
            response_data = await process_single_image(imageLink, prompt, username)
            end_time = datetime.now()
            response_data["total_processing_time"] = str((end_time - start_time).total_seconds())

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_image(image_link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_link) as response:
            image_data = await response.read()
            return Image.open(BytesIO(image_data))

async def process_single_image(image_link: str, prompt: str, username: str):
    raw_image = await fetch_image(image_link)

    # Prepare the inputs
    formatted_prompt = f"<image>\n{prompt}\nASSISTANT:"
    inputs = processor(formatted_prompt, raw_image, return_tensors='pt').to(device)

    # Generate the output
    start_time = datetime.now()
    output = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Decode the response
    response = processor.decode(output[0], skip_special_tokens=True)
    unique_id = str(uuid.uuid4())
    # Save the response to a JSON file
    response_data = {
        "id" :str(unique_id),
        "url": image_link,
        "prompt": prompt,
        "response": response,
        "username": username,
        "processing_time": str(processing_time),
        "time": str(datetime.now())
    }
    with open("response.json", "a") as f:
        json.dump(response_data, f)
        f.write("\n")
    try:
        with open("static/chat_history.json", "r") as file:
            try:
                chat_history = json.load(file)
            except json.JSONDecodeError:
                chat_history = []
    except FileNotFoundError:
        chat_history = []

    # Append the new chat to the chat history
    chat_history.insert(0,response_data)

    # Save the updated chat history back to file or database
    with open("static/chat_history.json", "w") as file:
        json.dump(chat_history, file)
        
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
