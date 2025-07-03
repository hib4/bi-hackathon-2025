from schema.book_schema import create_book_schema
from utils.ai import get_prompt_schema,ask_sealion

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
    return {
        "data": result,
        "user": current_user
    }