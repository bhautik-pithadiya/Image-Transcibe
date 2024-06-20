import requests
from PIL import Image
from fastapi import FastAPI, HTTPException, Request, Form,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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
from fastapi.responses import JSONResponse
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

origins = [
    "http://localhost",
    "http://0.0.0.0",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://ec2-44-208-238-252.compute-1.amazonaws.com:5500"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

model_path = 'model/'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model and processor
model = LlavaForConditionalGeneration.from_pretrained(
    model_path      
)

processor = AutoProcessor.from_pretrained(model_path)
logger.info("Model Loaded")


IMAGE_PATH = 'data/images/'
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

@app.post("/")
async def process_image(imageSource: str = Form(None),imageLink: str = Form(None), imageUpload: UploadFile = File(None), prompt: str = Form(...), username: str = Form(...)):
    
    try:
        if imageSource == 'link' and imageLink:
            unique_id = str(uuid.uuid4())
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
                response_data = await process_single_image(imageLink, prompt, username,unique_id)
                end_time = datetime.now()
                response_data["total_processing_time"] = str((end_time - start_time).total_seconds())
                
        elif imageSource == 'upload' and imageUpload:
            unique_id = str(uuid.uuid4())
            response_data = {}  
            logger.info(f"Received form data - ImageUpload: {imageUpload.filename}, Prompt: {prompt}, Username: {username}")
            raw_image = Image.open(imageUpload.file)
            
            ## save_image 
            save_path = os.path.join(IMAGE_PATH,f"{unique_id}.jpg")
            raw_image.save(save_path)
            response_data = await process_uploaded_image(raw_image, prompt, username,unique_id)
            
        else:
            response_data =  HTTPException(status_code=400, detail="Invalid image source or missing data.")
            raise response_data
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_image(image_link: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_link) as response:
            image_data = await response.read()
            return Image.open(BytesIO(image_data))
        
async def process_uploaded_image(raw_image: Image, prompt: str, username: str,unique_id:str):
    formatted_prompt = f"<image>\n{prompt}\nASSISTANT:"
    inputs = processor(formatted_prompt, raw_image, return_tensors='pt').to(device)

    start_time = datetime.now()
    output = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    response = processor.decode(output[0], skip_special_tokens=True)
    
    response_data = {
        "id": unique_id,
        "prompt": prompt,
        "response": response,
        "username": username,
        "processing_time": str(processing_time),
        "time": str(datetime.now())
    }
    
    save_data(response_data)
    
    return response_data


async def process_single_image(image_link: str, prompt: str, username: str,unique_id:str):
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
    
    save_data(response_data)
    return response_data

def save_data(response_data):
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

@app.get("/chat_history")
async def get_chat_history():
    json_file_path = "static/chat_history.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            data = json.load(file)
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
