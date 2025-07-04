from schema.request.book_schema import create_book_schema
from utils.sea_lion import get_prompt_schema,ask_sealion
from utils.flux_1_schnell import generate_multiple_image

async def create_book(body: create_book_schema, current_user):
    prompt = body.prompt
    language = body.language
    length = body.length

    prompt_schema = get_prompt_schema(
        description=prompt,
        language=language,
        length=length
    )
    result = await ask_sealion(prompt_schema)
    book = result.get("book")
    image_prompts = []

    image_prompts.append({
        "key": "coverImage",
        "prompt": book.get("coverImage"),
    })

    for page in book.get("pages",[]):
        page_number = page.get("pageNumber")
        image_prompts.append({
            "key": f"page_{page_number}",
            "prompt": page.get("image"),
        })

    generate_images = await generate_multiple_image(image_prompts=image_prompts)

    return {
        "data": book,
        "user": current_user,
        "images": generate_images
    }