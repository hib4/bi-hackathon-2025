from fastapi import HTTPException
from schema.request import book_schema
from models.book import Book
from utils.ai.concurrent import generate_multiple_image_and_voice_concurrently
import json

dummy_scene_json = None
with open("./handler/scene_sample.json", "r", encoding="utf-8") as f:
    dummy_scene_json = json.load(f)

async def create_book(body: book_schema.create_book_schema, current_user):
    prompt = body.prompt
    language = body.language

    book = Book(
        user_id= current_user.get("id"),
        title= dummy_scene_json.get("title"),
        theme= dummy_scene_json.get("theme"),
        age_group= dummy_scene_json.get("age_group"),
        language= dummy_scene_json.get("language"),
        status= dummy_scene_json.get("status"),
        current_scene= dummy_scene_json.get("current_scene"),
        started_at= dummy_scene_json.get("started_at"),
        finished_at= dummy_scene_json.get("finished_at"),
        maximum_point= dummy_scene_json.get("maximum_point"),
        story_flow= dummy_scene_json.get("story_flow"),
        characters= dummy_scene_json.get("characters"),
        scene= dummy_scene_json.get("scene"),
        user_story= dummy_scene_json.get("user_story")
    )

    #await book.insert()

    scenes = book.scene

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

    return {
        "message": "successfully create new book",
        "data":{
            "result": result
            #"id": str(book.id)
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
    return {
        "data": dummy_scene_json
    }