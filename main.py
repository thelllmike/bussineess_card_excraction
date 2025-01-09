import os
import json
import logging
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from extract import extract_text_from_image, restructure_extracted_text_to_json
from database import Base, engine
from routers.prospect_router import router as prospect_router
from models.prospect_model import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variable for OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Configure CORS (update for production to restrict origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Create tables automatically at startup
    Base.metadata.create_all(bind=engine)

app.include_router(prospect_router)

@app.get("/")
async def read_root():
    """Root endpoint for basic API info."""
    return {"message": "Welcome to the Business Card Text Extraction API"}

@app.post("/extract_text")
async def extract_text(image: UploadFile = File(...)):
    """
    Extract text from an uploaded image file using OCR and restructure it to JSON format.
    """
    if image.content_type.split("/")[0] != "image":
        logger.error("Invalid file type uploaded")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")
    
    try:
        image_data = await image.read()
        logger.info("Image uploaded and read successfully")

        # Perform OCR and restructure the extracted text
        extracted_text = extract_text_from_image(image_data)
        restructured_text = restructure_extracted_text_to_json(extracted_text)

        logger.info("Text extracted and structured successfully")
        return JSONResponse(status_code=200, content={
            "message": "Text extracted successfully.",
            "extracted_text": extracted_text,
            "final_data": restructured_text
        })
    except Exception as e:
        logger.error(f"Failed to extract text: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract text from the image")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
