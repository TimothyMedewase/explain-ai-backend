from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status
from typing import List, Optional
import traceback
import logging
from app.file_utils import extract_text_from_file
from app.rag_engine import process_user_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process", status_code=status.HTTP_200_OK)
async def process(
    files: List[UploadFile] = File(...),
    query: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    try:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files were uploaded. Please upload at least one file."
            )
            
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Too many files. Maximum allowed is 5 files."
            )
            
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty. Please provide a question about the documents."
            )
            
        texts = []
        for file in files:
            content = await extract_text_from_file(file)
            texts.append(content)

        response_data = process_user_query(query, texts, conversation_id)
        return {
            "response": response_data["answer"], 
            "conversation_id": response_data["conversation_id"],
            "content_type": response_data.get("content_type", "general")  # Include the content type in the response
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/process")
async def process_get(query: str = Query(..., description="Your question about the content")):
    try:
        return {
            "message": "This endpoint requires a POST request with file uploads. Please use the POST method and include your files.",
            "example_usage": "POST to /process with 'files' (multipart/form-data) and 'query' parameters"
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing request: {str(e)}")
