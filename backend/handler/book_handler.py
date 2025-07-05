from fastapi import HTTPException
from schema.request import book_schema
from collections import defaultdict
from models.book import Book
from utils.ai.concurrent import generate_multiple_image_and_voice_concurrently
import json

dummy_scene_json = None
with open("./handler/scene_sample.json", "r", encoding="utf-8") as f:
    dummy_scene_json = json.load(f)

async def create_book(body: book_schema.create_book_schema, current_user):
    prompt = body.prompt
    language = body.language

    # fetch to scene builder ai
    book = dummy_scene_json

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
        started_at= book.get("started_at"),
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
            # "result": book
            "id": str(new_book.id)
        }
    }

async def get_books(current_user):
    books = await Book.find(Book.user_id == current_user.get("id")).to_list()
    return {
        "data": books
    }

async def get_book_by_id(id: str, current_user):
    book = await Book.get(id)
    if not book:
        raise HTTPException(status_code= 404, detail= f"book with id {id} not found")
    
    user_id = current_user.get("id")
    if book.user_id != user_id:
        raise HTTPException(status_code= 403, detail= f"book with id {id} not belong to user with id ${user_id}")

    return {
        "data": dummy_scene_json
    }