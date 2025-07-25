from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
import json
from rag import FinancialLiteracyRAG
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

# Request models
class StoryRequest(BaseModel):
    query: str = Field(..., description="Story request in Indonesian", example="Cerita tentang menabung")
    user_id: str = Field(..., example="user123")
    age: int = Field(..., example=7, description="Age of the child")

# Response models
class Character(BaseModel):
    name: str
    description: str

class Choice(BaseModel):
    choice: str
    content: str
    moral_value: str
    point: int
    next_scene: int

class Scene(BaseModel):
    scene_id: int
    type: str  # "narrative", "decision_point", "ending"
    img_url: Optional[str] = None
    img_description: Optional[str] = None
    voice_url: Optional[str] = None
    content: str
    next_scene: Optional[int] = None
    branch: Optional[List[Choice]] = None
    lesson_learned: Optional[str] = None
    selected_choice: Optional[str] = None  # For decision_point scenes

class StoryResponse(BaseModel):
    user_id: str
    title: str
    theme: List[str]
    language: str
    status: str
    age_group: int
    current_scene: int
    created_at: Optional[str] = None
    finished_at: Optional[str] = None
    maximum_point: int
    story_flow: Dict[str, Any]
    characters: List[Character]
    scene: List[Scene]
    user_story: Dict[str, Any]
    cover_img_url: Optional[str] = None
    cover_img_description: Optional[str] = ""
    description: str = "A story about financial literacy for children."
    estimated_reading_time: int = 600  # Default to 5 minutes in seconds

# Create FastAPI instance
app = FastAPI(
    title="Indonesian Financial Literacy Storytelling API",
    description="Generate interactive stories for children's financial education",
    version="1.0.0"
)

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize your RAG system
rag = FinancialLiteracyRAG(
    data_dir='./knowledge_base',
    persist_directory='./chroma_db'
)
rag.initialize_rag(rebuild=True)

chat_model = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

def convert_age_to_range(age: int) -> str:
    """Convert single age to age range format for RAG system"""
    if age <= 5:
        return "4-5"
    elif age <= 7:
        return "6-7"
    elif age <= 9:
        return "7-9"
    elif age <= 12:
        return "10-12"
    else:
        return "7-9"  # Default fallback

def validate_story_content(story_data: dict, user_id: str, age: int):
    """
    Comprehensive validation and standardization of story content to match exact JSON structure
    """
    
    # 1. Ensure all top-level required fields exist
    required_top_level_fields = {
        "user_id": user_id,
        "title": "Untitled Story",
        "theme": [],
        "language": "indonesian",
        "status": "in_progress",
        "age_group": age,  # Keep as int since you changed it
        "current_scene": 1,
        "created_at": None,
        "finished_at": None,
        "maximum_point": 10,
        "characters": [],
        "scene": [],
        "cover_img_url": None,
        "cover_img_description": "",
        "description": "A story about financial literacy for children.",
        "estimated_reading_time": 3600
    }
    
    for field, default_value in required_top_level_fields.items():
        if field not in story_data:
            if field == "user_id":
                story_data[field] = user_id
            elif field == "age_group":
                story_data[field] = age
            else:
                story_data[field] = default_value
    
    # 2. Ensure story_flow structure exists and is populated correctly
    if "story_flow" not in story_data:
        story_data["story_flow"] = {
            "total_scene": 0,
            "decision_point": [],
            "ending": []
        }
    
    # 3. Ensure user_story structure exists
    if "user_story" not in story_data:
        story_data["user_story"] = {
            "visited_scene": [],
            "choices": [],
            "total_point": 0,
            "finished_time": 0
        }
    
    # 4. Validate and standardize scenes
    scenes = story_data.get("scene", [])
    if not scenes:
        raise HTTPException(status_code=500, detail="No scenes found in story")
    
    decision_points = []
    endings = []
    
    for i, scene in enumerate(scenes):
        # Ensure required scene fields
        scene_required_fields = {
            "scene_id": i + 1,
            "type": "narrative",
            "img_url": None,
            "img_description": "",
            "voice_url": None,
            "content": "",
        }
        
        for field, default_value in scene_required_fields.items():
            if field not in scene:
                scene[field] = default_value
        
        # Validate scene type and structure based on type
        scene_type = scene.get("type", "narrative")
        
        if scene_type == "narrative":
            # Narrative scenes: must have next_scene, must NOT have branch or lesson_learned
            if "branch" in scene:
                del scene["branch"]
            if "lesson_learned" in scene:
                del scene["lesson_learned"]
            if "selected_choice" in scene:
                del scene["selected_choice"]
            if "next_scene" not in scene:
                # Set next scene to scene_id + 1, or None if it's the last scene
                if i < len(scenes) - 1:
                    scene["next_scene"] = scene["scene_id"] + 1
                else:
                    scene["next_scene"] = None
        
        elif scene_type == "decision_point":
            # Decision point scenes: must have branch, must NOT have next_scene or lesson_learned
            if "next_scene" in scene:
                del scene["next_scene"]
            if "lesson_learned" in scene:
                del scene["lesson_learned"]
            
            # Validate branch structure
            if "branch" not in scene:
                raise HTTPException(status_code=500, detail=f"Decision point scene {scene['scene_id']} missing 'branch'")
            
            branch = scene["branch"]
            if not isinstance(branch, list) or len(branch) != 2:
                raise HTTPException(status_code=500, detail=f"Decision point scene {scene['scene_id']} must have exactly 2 choices")
            
            # Validate each choice in branch
            for j, choice in enumerate(branch):
                choice_required_fields = {
                    "choice": "baik" if j == 0 else "buruk",
                    "content": "",
                    "moral_value": "",
                    "point": 0,
                    "next_scene": scene["scene_id"] + 1
                }
                
                for field, default_value in choice_required_fields.items():
                    if field not in choice:
                        choice[field] = default_value
            
            # Add to decision points list
            decision_points.append(scene["scene_id"])
            
            # Ensure selected_choice exists
            if "selected_choice" not in scene:
                scene["selected_choice"] = None
        
        elif scene_type == "ending":
            # Ending scenes: must have lesson_learned, must NOT have next_scene or branch
            if "next_scene" in scene:
                del scene["next_scene"]
            if "branch" in scene:
                del scene["branch"]
            if "selected_choice" in scene:
                del scene["selected_choice"]
            
            if "lesson_learned" not in scene:
                scene["lesson_learned"] = "Pelajaran penting tentang keuangan."
            
            # Add to endings list
            endings.append(scene["scene_id"])
        
        else:
            raise HTTPException(status_code=500, detail=f"Invalid scene type: {scene_type}")
    
    # 5. Update story_flow with correct information
    story_data["story_flow"]["total_scene"] = len(scenes)
    story_data["story_flow"]["decision_point"] = decision_points
    story_data["story_flow"]["ending"] = endings
    
    # 6. Validate characters structure
    characters = story_data.get("characters", [])
    for character in characters:
        if "name" not in character:
            character["name"] = "Character"
        if "description" not in character:
            character["description"] = "A character in the story"
    
    # 7. Ensure maximum_point is an integer
    if not isinstance(story_data.get("maximum_point"), int):
        # Calculate maximum point from all positive points in choices
        max_points = 0
        for scene in scenes:
            if scene.get("type") == "decision_point" and "branch" in scene:
                for choice in scene["branch"]:
                    point = choice.get("point", 0)
                    if isinstance(point, int) and point > 0:
                        max_points += point
        story_data["maximum_point"] = max_points if max_points > 0 else 10
    
    return story_data

@app.post("/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    try:
        # Create prompt using your RAG system - convert age to range for RAG
        prompt = rag.create_prompt(
            query=request.query,
            user_id=request.user_id,
            age=request.age,
        )
        
        # Get response from LLM
        response = chat_model.invoke(prompt)
        
        # Clean and parse JSON
        story_json = clean_json_response(response.content)
        
        # Validate and standardize the story content
        story_json = validate_story_content(story_json, request.user_id, request.age)
        
        print(f"Generated story for user {request.user_id} with age {request.age}: {story_json['title']}")
        return StoryResponse(**story_json)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

def clean_json_response(content: str) -> dict:
    """Clean and parse JSON from LLM response"""
    import re
    
    # Remove markdown formatting
    if "```json" in content:
        content = re.search(r'```json\n(.*?)\n```', content, re.DOTALL).group(1)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from AI: {str(e)}")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Indonesian Financial Literacy API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)