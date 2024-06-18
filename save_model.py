import torch
from transformers import LlavaForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig

# Configuration for double quantization
double_quant_config = BitsAndBytesConfig(
    load_in_4bit=True, 
    bnb_4bit_use_double_quant=True, 
    bnb_4bit_compute_dtype=torch.float16
)

# Load the original model
model_id = "llava-hf/llava-1.5-7b-hf"
model = LlavaForConditionalGeneration.from_pretrained(
    model_id,
    quantization_config=double_quant_config
)

# Quantize the model
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Save the quantized model
model.save_pretrained("model/")

# Save the processor
processor = AutoProcessor.from_pretrained(model_id)
processor.save_pretrained("model/")
