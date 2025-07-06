from fastapi.concurrency import run_in_threadpool
from utils.azure_blob_storage import upload_file_to_blob
from openai import OpenAI
from settings import settings
from uuid import uuid4
import json

FLUX_1_SCHNELL_HOST = "https://api.studio.nebius.com/v1/"
FLUX_1_SCHNELL_MODEL = "black-forest-labs/flux-schnell"
FLUX_1_SCHNELL_IMAGE_RESPONSE_FORMAT = "b64_json" # b64_json or url
IMAGE_FOLDER_NAME = "images"

client = OpenAI(
    base_url=FLUX_1_SCHNELL_HOST,
    api_key=settings.FLUX_1_SCHNELL_API_KEY
)

def _generate_image(image_prompt):
    scene_id = image_prompt.get("scene_id") or 1
    prompt = image_prompt.get("prompt")
    image_type = image_prompt.get("type")

    response = client.images.generate(
        model=FLUX_1_SCHNELL_MODEL,
        response_format=FLUX_1_SCHNELL_IMAGE_RESPONSE_FORMAT,
        extra_body={
            "response_extension": "png",
            "width": 512,
            "height": 512,
            "num_inference_steps": 4,
            "negative_prompt": "",
            "seed": -1,
            "loras": None
        },
        prompt= f"{prompt}. Explcit instruction: cartoon style, used for kids, be family friendly"
    )
    json_result = json.loads(response.to_json())
    image_result = json_result.get("data")[0]
    b64_string = image_result.get("b64_json")
    url = image_result.get("url")

    if b64_string:
        unique_id =  str(uuid4())
        url = upload_file_to_blob(
            base64_string=b64_string,
            folder_name=IMAGE_FOLDER_NAME,
            blob_filename= f"{unique_id}.png"
        )

    if image_type == "cover_image":  
        return {
            "scene_id": scene_id,
            "type": "cover_image",
            "cover_image": url
        }

    return { 
        "scene_id": scene_id,
        "type": "image",
        "image": url
    }

async def generate_image(image_prompt):
    return await run_in_threadpool(_generate_image, image_prompt)
