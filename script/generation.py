from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

def load_falcon_model():
    """Load Falcon-RW-1B model on CPU"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "..", "models", "falcon-rw-1b")
    model_path = os.path.abspath(model_path)
    
    print(f"Looking for model at: {model_path}")
    
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
    
    required_files = ['config.json', 'pytorch_model.bin']
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file missing: {file_path}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=None,  
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True  
    )
    
    
    model = model.to("cpu")
    return tokenizer, model

def generate_answer(prompt, tokenizer, model):
    """Generate answer with Falcon on CPU"""
    inputs = tokenizer(
        prompt, 
        return_tensors="pt", 
        max_length=2048, 
        truncation=True,
        padding=True
    )
    
    
    inputs = {k: v.to("cpu") for k, v in inputs.items()}
    
    with torch.no_grad():  
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1  
        )
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    
    if "<|assistant|>" in full_response:
        return full_response.split("<|assistant|>")[-1].strip()
    
    
    if prompt in full_response:
        return full_response.replace(prompt, "").strip()
    
    return full_response