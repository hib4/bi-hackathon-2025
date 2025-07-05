from utils.ai.flux_1_schnell import generate_image
from utils.ai.text_to_speech import synthesize_speech
import asyncio

async def generate_multiple_image_and_voice_concurrently(requests):
    tasks = []

    # uncomment the code line below to save cloud credit for image and voice generation
    # requests = requests[:2]

    for request in requests:
        request_type = request.get("type")

        if request_type == "image":
            tasks.append(generate_image(request))

        if request_type == "voice":
            tasks.append(synthesize_speech(request))

    return await asyncio.gather(*tasks)
