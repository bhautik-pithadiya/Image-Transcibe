import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from transformers import BitsAndBytesConfig
import json
from datetime import datetime

model_path = 'model/'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model and processor
# with open(model_path,'r') as file:
#     config = json.load(file)

# print(config['_name_or_path'])

model = LlavaForConditionalGeneration.from_pretrained(model_path)
processor = AutoProcessor.from_pretrained(model_path)
logger.info("Model Loaded")