from fastapi.concurrency import run_in_threadpool
from settings import settings
from openai import OpenAI
import json

SEALION_HOST = "https://api.sea-lion.ai/v1"
SEALION_MODEL = "aisingapore/Llama-SEA-LION-v3-70B-IT"
SEALION_TEMPERATURE = 0.7

client = OpenAI(
    api_key=settings.SEALION_API_KEY,
    base_url=SEALION_HOST
)

def get_prompt_schema(description, language, length):
    return f"""
        {{
            "description": "generate an interactive book for kids and you must make it {length} PAGES, create with instructed page number and with description: '{description}', with language: '{language}', Answer this question with this JSON Schema for your respond, strictly write in JSON only as your respond will directly parse to JSON object so make sure your respond is valid JSON. dont write ```json ``` just pure JSON text",
            "type": "object",
            "property": {{
                "book": {{
                    "description": "this is an book object",
                    "type": "object",
                    "property": {{
                        "title": {{
                            "description": "the title of the book",
                            "type": "string"
                        }},
                        "description": {{
                            "description": "the short and summarize description of the book",
                            "type": "string"
                        }},
                        "pages": {{
                            "description": "the pages inside of book",
                            "type": "array",
                            "property": {{
                                "content": {{
                                    "description": "text content inside one page, write in 100 - 200 characters, make it excited for kids, also each page must align and continue, like you are the mother that read this story for her kids",
                                    "type": "string",
                                }},
                                "image": {{
                                    "description": "write this only in English!, description of the image used for the page, this description will be used to generate cover image using text to image ai model, make sure write to the point and easy to understand for the AI to generate cover image",
                                    "type": "string",
                                }},
                                "pageNumber": {{
                                    "description": "the page number",
                                    "type": "number",
                                }}
                            }},
                            "required": ["content", "image", "pageNumber"]
                        }},
                        
                        "quiz": {{
                            "description": "this is quiz for the kids to learn, make the quiz very excited",
                            "type": "object",
                            "property": {{
                                "question": {{
                                    "description": "quiz question for the kid to learn, make it engaging, with multiple choise for kids to choose",
                                    "type": "string",
                                }},
                                "answerA": {{
                                    "description": "answer for choise A",
                                    "type": "string",
                                }},
                                "answerB": {{
                                    "description": "answer for choise B",
                                    "type": "string",
                                }},
                                "answerC": {{
                                    "description": "answer for choise C",
                                    "type": "string",
                                }},
                                "correctAnswer": {{
                                    "description": "the correct answer, write with option of: ['answerA','answerB' or 'answerC']",
                                    "type": "string",
                                }}
                            }},
                            "required": ["question", "answerA", "answerB", "answerC", "correctAnswer"]
                        }},
                        "coverImage": {{
                            "description": "write this only in English! ,write short description about the cover image, this description will be used to generate cover image using text to image ai model, make sure write to the point and easy to understand for the AI to generate cover image",
                            "type": "string"
                        }}
                    }},
                    "required": ["title","description","pages","quiz","coverImage"]
                }}
            }},
            "required": "book"
        }}
    """

def _ask_sync(prompt: str) -> dict:
    response = client.chat.completions.create(
        model=SEALION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=SEALION_TEMPERATURE
    )
    text_response = response.choices[0].message.content
    json_string = text_response

    if "```json" in json_string or "```" in json_string:
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        
    return json.loads(json_string)

async def ask_sealion(prompt: str) -> dict:
    return await run_in_threadpool(_ask_sync, prompt)