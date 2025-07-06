from utils.ai.concurrent import generate_multiple_image_and_voice_concurrently
from utils.api_request import post
from fastapi import HTTPException
from settings import settings
from schema.request import book_schema
from schema.response.book_card import Book_Card
from collections import defaultdict
from models.book import Book
from datetime import timedelta
import json

dummy_scene_json = None
with open("./handler/scene_sample.json", "r", encoding="utf-8") as f:
    dummy_scene_json = json.load(f)

book_stort_generation_url = settings.BOOK_STORY_GENERATION_URL

async def create_book(body: book_schema.create_book_schema, current_user):
    query = body.query
    age = body.age

    # fetch to book_stort_generation_url
    book = await post(
        url= f"{book_stort_generation_url}/generate-story",
        body= {
            "query": query,
            "user_id": current_user.get("id"),
            "age": age
        }
    )

    scenes = book.get("scene")
    extracted_scenes = [
        {
            "scene_id": scene.get("scene_id"),
            "img_description": scene.get("img_description"),
            "content": scene.get("content")
        }
        for scene in scenes
    ]

    requests = []
    for extracted_scene in extracted_scenes:
        requests.append({
            "scene_id": extracted_scene.get("scene_id"),
            "type": "image",
            "prompt": extracted_scene.get("img_description")
        })
        requests.append({
            "scene_id": extracted_scene.get("scene_id"),
            "type": "voice",
            "prompt": extracted_scene.get("content")
        })

    result = await generate_multiple_image_and_voice_concurrently(requests)

    scene_data = defaultdict(list)
    for item in result:
        scene_data[item["scene_id"]].append(item)

    for scene in book.get("scene"):
        scene_id = scene.get("scene_id")

        items = scene_data.get(scene_id, [])

        image_url = next((i["image"] for i in items if i["type"] == "image"), None)
        voice_url = next((i["voice"] for i in items if i["type"] == "voice"), None)
        
        if image_url:
            scene["img_url"] = image_url

        if voice_url:
            scene["voice_url"] = voice_url

    new_book = Book(
        user_id= current_user.get("id"),
        title= book.get("title"),
        theme= book.get("theme"),
        age_group= book.get("age_group"),
        language= book.get("language"),
        status= book.get("status"),
        current_scene= book.get("current_scene"),
        finished_at= book.get("finished_at"),
        maximum_point= book.get("maximum_point"),
        story_flow= book.get("story_flow"),
        characters= book.get("characters"),
        scene= book.get("scene"),
        user_story= book.get("user_story")
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

def _format_book_cards(books: list) -> list:
    book_cards = []
    for book in books:
        book_card = Book_Card(
            id= str(book.id),
            title= book.title,
            short_description= book.title, # TODO switch to real description
            language= book.language,
            img_cover_url="",
            Estimation_time_to_read= "43 minutes",
            created_at= str(book.created_at)
        )
        book_cards.append(book_card)
    return book_cards

def _time_estimation_format(duration: timedelta):
    total_seconds = int(duration.total_seconds())

    hours,reminder = divmod(total_seconds,3600)
    minutes,seconds = divmod(reminder,60)

    time_estimate = ""

    if not hours:
        time_estimate += f"{hours} hours"
    if not minutes:
        time_estimate += f"{minutes} minutes"
    if not seconds:
        time_estimate += f"{seconds} seconds"
    return time_estimate
