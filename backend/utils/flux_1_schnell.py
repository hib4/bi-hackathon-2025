from fastapi.concurrency import run_in_threadpool
from openai import OpenAI
from settings import settings
import asyncio
import json

FLUX_1_SCHNELL_HOST = "https://api.studio.nebius.com/v1/"
FLUX_1_SCHNELL_MODEL = "black-forest-labs/flux-schnell"

client = OpenAI(
    base_url=FLUX_1_SCHNELL_HOST,
    api_key=settings.FLUX_1_SCHNELL_API_KEY
)

def _generate_image(image_prompt):
    key = image_prompt.get("key")
    prompt = image_prompt.get("prompt")

    response = client.images.generate(
        model=FLUX_1_SCHNELL_MODEL,
        response_format="b64_json",
        extra_body={
            "response_extension": "png",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 4,
            "negative_prompt": "",
            "seed": -1,
            "loras": None
        },
        prompt= f"{prompt} cartoon style, used for kids"
    )
    image_result = json.loads(response.to_json())
    return { 
        "key": key,
        "image": image_result.get("data").get("b64_json") 
    }

async def generate_image(image_prompt):
    return await run_in_threadpool(_generate_image, image_prompt)

async def generate_multiple_image(image_prompts):
    tasks = []
    for image_prompt in image_prompts:
        tasks.append(generate_image(image_prompt))
    return await asyncio.gather(*tasks)