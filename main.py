import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import Optional

from app.schemas.models import HTMLExtractRequest, ExtractResponse
from app.extractor.html_parser import fetch_and_parse_html
from app.extractor.pdf_parser import extract_text_from_pdf
from app.extractor.llm_engine import convert_to_markdown, extract_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Structured Document Extraction API", version="1.0.0")

@app.post("/extract/html", response_model=ExtractResponse)
async def extract_html(request: HTMLExtractRequest):
    try:
        # Preprocessing
        if request.url:
            text_content = fetch_and_parse_html(url=str(request.url))
        elif request.raw_html:
            text_content = fetch_and_parse_html(raw_html=request.raw_html)
        else:
            raise HTTPException(status_code=400, detail="Must provide either url or raw_html")
        
        # LLM Processing
        markdown_output = convert_to_markdown(text_content)
        json_output = extract_json(text_content, use_schema=request.use_schema)
        
        return ExtractResponse(markdown=markdown_output, json_data=json_output)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/pdf", response_model=ExtractResponse)
async def extract_pdf(
    file: UploadFile = File(...),
    use_schema: bool = Form(False)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    try:
        # Read file
        file_bytes = await file.read()
        
        # Preprocessing
        text_content = extract_text_from_pdf(file_bytes)
        
        if not text_content:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF")
            
        # LLM Processing
        markdown_output = convert_to_markdown(text_content)
        json_output = extract_json(text_content, use_schema=use_schema)
        
        return ExtractResponse(markdown=markdown_output, json_data=json_output)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
