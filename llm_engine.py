import os
import json
from openai import OpenAI
from pydantic import BaseModel
from app.schemas.models import ArticleSchema

# Initialize the OpenAI client
# For Qwen3-VL or other models, you might set OPENAI_BASE_URL
# Example: export OPENAI_BASE_URL="http://localhost:8000/v1"
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "dummy_key"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-vl")

def _get_llm_response(system_prompt: str, user_prompt: str, response_format=None) -> str:
    """Helper to call the LLM."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    kwargs = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
    }
    
    if response_format:
        kwargs["response_format"] = response_format

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"LLM Processing failed: {str(e)}")

def convert_to_markdown(text: str) -> str:
    """Converts raw text/HTML to clean markdown using LLM."""
    system_prompt = "You are a professional document formatter. Your task is to convert the provided text into clean, well-structured Markdown. Preserve the logical hierarchy, headings, and lists."
    user_prompt = f"Convert the following text to Markdown:\n\n{text}"
    
    return _get_llm_response(system_prompt, user_prompt)

def extract_json(text: str, use_schema: bool = False) -> dict:
    """Extracts JSON from text, optionally enforcing a predefined schema."""
    if use_schema:
        schema_json = ArticleSchema.model_json_schema()
        system_prompt = (
            "You are a structured data extraction AI. Extract the information from the user's text and output "
            f"a JSON object that strictly adheres to the following JSON schema:\n\n{json.dumps(schema_json)}\n\n"
            "Return ONLY valid JSON. Do not include markdown code blocks or any other text."
        )
    else:
        system_prompt = (
            "You are an intelligent data extraction AI. Analyze the provided text and extract the most important "
            "entities, relationships, and key metrics into a well-structured JSON object. Automatically infer the best schema. "
            "Return ONLY valid JSON. Do not include markdown code blocks or any other text."
        )

    user_prompt = f"Extract structured data from the following text:\n\n{text}"
    
    response_text = _get_llm_response(system_prompt, user_prompt, response_format={"type": "json_object"})
    
    # Clean up response in case the model returns markdown formatting (e.g. ```json ... ```)
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"raw_extraction": response_text}
