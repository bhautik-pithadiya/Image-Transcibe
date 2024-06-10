import torch
import numpy as np
from transformers import AutoProcessor, LlavaForConditionalGeneration
from transformers import BitsAndBytesConfig

double_quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True)


# Define device
print('Imported')
device = 'cpu' #torch.device("cuda" if torch.cuda.is_available() else "cpu")
print('Device', device)

model_id = "llava-hf/llava-1.5-7b-hf"
print('************** Lading Model *************** ')
model = LlavaForConditionalGeneration.from_pretrained(model_id,quantization_config=double_quant_config)
print('*************** Model Loaded ***************')
processor = AutoProcessor.from_pretrained(model_id)
