import fitz  
from fastapi import UploadFile
import logging


logger = logging.getLogger(__name__)

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded files, with special handling for PDFs and binary files."""
    try:
        if file.filename.endswith(".pdf"):
            pdf_bytes = await file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
            await file.seek(0)
            return text
        elif file.content_type and file.content_type.startswith("text/"):
            # For text files
            text = await file.read()
            await file.seek(0)
            return text.decode("utf-8", errors="replace")
        else:
            # For binary files, just return the filename as we can't extract text
            logger.warning(f"Cannot extract text from binary file: {file.filename}, content-type: {file.content_type}")
            return f"Binary file: {file.filename} (Content type: {file.content_type})"
    except Exception as e:
        logger.error(f"Error extracting text from {file.filename}: {str(e)}")
        return f"Error processing file {file.filename}: {str(e)}"
