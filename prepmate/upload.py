
from fastapi import APIRouter, UploadFile, File
from typing import List
import logging
from converter import process_uploaded_files

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    """
    Accept multiple uploaded files and return the vector format output, with logging for testing.
    """
    logging.info(f"Received {len(files)} file(s) for processing.")
    for file in files:
        logging.info(f"Processing file: {file.filename}")
    try:
        result = await process_uploaded_files(files)
        logging.info(f"Processing complete. Chunks created: {result.get('chunks_created')}")
        logging.info(f"Vectorstore saved at: {result.get('vectorstore_path')}")
        return result
    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return {"error": str(e)}
