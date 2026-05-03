from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, Union

class HTMLExtractRequest(BaseModel):
    url: Optional[HttpUrl] = Field(None, description="The URL to fetch HTML from")
    raw_html: Optional[str] = Field(None, description="Raw HTML string if URL is not provided")
    use_schema: bool = Field(False, description="Whether to extract JSON using the predefined schema")

class ExtractResponse(BaseModel):
    markdown: str
    json_data: Optional[Dict[str, Any]] = None

class ArticleSchema(BaseModel):
    title: str = Field(..., description="Title of the extracted content")
    author: Optional[str] = Field(None, description="Author or source if available")
    key_points: list[str] = Field(..., description="List of key points extracted from the content")
    summary: str = Field(..., description="A short summary of the content")
