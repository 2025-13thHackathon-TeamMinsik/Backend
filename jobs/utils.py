from diffusers import StableDiffusionPipeline
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import torch

HF_TOKEN = settings.HUGGINGFACE_TOKEN

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    use_auth_token=HF_TOKEN
).to("cpu")  
pipe.enable_attention_slicing()  

def generate_image_from_description(description):
    #공고 description을 기반으로 AI 이미지 생성
    image = pipe(description).images[0]  
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

def save_image_to_jobpost(jobpost, image_data):
    jobpost.image_from_ai.save(f"jobpost_{jobpost.id}.png", ContentFile(image_data))
