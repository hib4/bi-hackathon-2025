from utils.ai.concurrent import generate_multiple_image_and_voice_concurrently
from utils.api_request import post
from fastapi import HTTPException
from settings import settings
from schema.request import book_schema
from schema.response.book_card import Book_Card
from collections import defaultdict
from models.book import Book
from utils.ai.text_to_speech import AVAILABLE_VOICES
import json

dummy_scene_json = None
with open("./handler/scene_sample.json", "r", encoding="utf-8") as f:
    dummy_scene_json = json.load(f)

book_stort_generation_url = settings.BOOK_STORY_GENERATION_URL

async def create_book(body: book_schema.create_book_schema, current_user):
    query = body.query
    age = body.age
    voice_name_code = body.voice_name_code

    if not voice_name_code in AVAILABLE_VOICES.keys():
        raise HTTPException(status_code= 400, detail= f"invalid language_code")

    # fetch to book_stort_generation_url
    book = await post(
        url= f"{book_stort_generation_url}/generate-story",
        body= {
            "query": query,
            "user_id": current_user.get("id"),
            "age": age
        }
    )

    # book = dummy_scene_json

    scenes = book.get("scene")
    extracted_scenes = [
        {
            "scene_id": scene.get("scene_id"),
            "img_description": scene.get("img_description"),
            "content": scene.get("content")
        }
        for scene in scenes
    ]

    cover_img_description = book.get("cover_img_description")
    characters = book.get("characters")

    requests = []
    requests.append({
        "scene_id": None,
        "type": "cover_image",
        "prompt": _add_character_description(
            characters=characters,
            img_description=cover_img_description
        )
    })

    for extracted_scene in extracted_scenes:
        img_description = extracted_scene.get("img_description")

        requests.append({
            "scene_id": extracted_scene.get("scene_id"),
            "type": "image",
            "prompt": _add_character_description(
                characters=characters,
                img_description=img_description
            )
        })
        requests.append({
            "scene_id": extracted_scene.get("scene_id"),
            "type": "voice",
            "voice_name_code": voice_name_code,
            "prompt": extracted_scene.get("content")
        })

    result = await generate_multiple_image_and_voice_concurrently(requests)

    scene_data = defaultdict(list)
    for item in result:
        scene_data[item["scene_id"]].append(item)

    for scene in book.get("scene"):
        scene_id = scene.get("scene_id")

        items = scene_data.get(scene_id, [])

        cover_image_url = next((i["cover_image"] for i in items if i["type"] == "cover_image"), None)
        image_url = next((i["image"] for i in items if i["type"] == "image"), None)
        voice_url = next((i["voice"] for i in items if i["type"] == "voice"), None)
        
        if image_url:
            scene["img_url"] = image_url

        if voice_url:
            scene["voice_url"] = voice_url

        if cover_image_url:
            book["cover_img_url"] = cover_image_url

    new_book = Book(
        title= book.get("title"),
        cover_img_url= book.get("cover_img_url"),
        description= book.get("description"),
        estimated_reading_time= book.get("estimated_reading_time"),
        theme= book.get("theme",None) or book.get("tema",None),
        age_group= book.get("age_group"),
        language= book.get("language"),
        status= book.get("status"),
        current_scene= book.get("current_scene"),
        finished_at= book.get("finished_at"),
        maximum_point= book.get("maximum_point"),
        story_flow= book.get("story_flow"),
        characters= book.get("characters"),
        scene= book.get("scene"),
        user_story= book.get("user_story"),
        user_id= current_user.get("id")
    )

    await new_book.insert()

    return {
        "message": "successfully create new book",
        "data":{
            "id": str(new_book.id)
        }
    }

async def get_books(current_user):
    books = await Book.find(Book.user_id == current_user.get("id")).to_list()
    return {
        "data": _format_book_cards(books)
    }

async def get_book_by_id(id: str, current_user):
    book = await Book.get(id)
    if not book:
        raise HTTPException(status_code= 404, detail= f"book with id {id} not found")
    
    user_id = current_user.get("id")
    if book.user_id != user_id:
        raise HTTPException(status_code= 403, detail= f"book with id {id} not belong to user with id ${user_id}")

    return {
        "data": book
    }

def _add_character_description(characters: list, img_description: str) -> str:
    prompt = f"description: {img_description}, cartoon style, this image is for kids, used for interactive book, be family friendly."

    names = [item["name"] for item in characters]
    descriptions = [item["description"] for item in characters]

    if img_description in names:
        prompt += " character description: "

    for description in descriptions:
        prompt += f"{description}, "

    if len(descriptions) > 0:
        prompt += "."

    return prompt

def _format_book_cards(books: list) -> list:
    book_cards = []
    for book in books:
        book_card = Book_Card(
            id= str(book.id),
            title= book.title,
            description= book.description,
            language= book.language,
            cover_img_url= book.cover_img_url,
            estimation_time_to_read= _time_estimation_format(book.estimated_reading_time),
            created_at= str(book.created_at)
        )
        book_cards.append(book_card)
    return book_cards

def _time_estimation_format(duration: int) -> str:    
    total_seconds = duration

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:  # Show 0 seconds if all others are zero
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return " ".join(parts)
