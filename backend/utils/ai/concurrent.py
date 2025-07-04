from utils.ai.flux_1_schnell import generate_image
import asyncio

async def generate_multiple_image_and_voice_concurrently(requests):
    tasks = []
    for request in requests:

        if request.get("type") == "image":
            tasks.append(generate_image(request))

        # if requests.get("type") == "audio":
        #     tasks.append(generate_image(request))

    return await asyncio.gather(*tasks)
