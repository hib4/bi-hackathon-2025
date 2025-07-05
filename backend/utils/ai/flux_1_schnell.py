from fastapi.concurrency import run_in_threadpool
from openai import OpenAI
from settings import settings
import json

FLUX_1_SCHNELL_HOST = "https://api.studio.nebius.com/v1/"
FLUX_1_SCHNELL_MODEL = "black-forest-labs/flux-schnell"

client = OpenAI(
    base_url=FLUX_1_SCHNELL_HOST,
    api_key=settings.FLUX_1_SCHNELL_API_KEY
)

def _generate_image(image_prompt):
    scene_id = image_prompt.get("scene_id")
    prompt = image_prompt.get("prompt")

    response = client.images.generate(
        model=FLUX_1_SCHNELL_MODEL,
        response_format="url",
        extra_body={
            "response_extension": "png",
            "width": 1024,
            "height": 1024,
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
    return { 
        "scene_id": scene_id,
        "type": "image",
        "image": b64_string or url
    }

async def generate_image(image_prompt):
    return await run_in_threadpool(_generate_image, image_prompt)
