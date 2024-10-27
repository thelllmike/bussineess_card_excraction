import os
import json
import base64
import logging
import requests
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from extract import extract_text_from_image  # Import your OCR function

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variable for OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="Business Card Text Extraction API",
    docs_url="/api/business_card_text_extraction/docs",
    redoc_url="/api/business_card_text_extraction/redoc",
    openapi_url="/api/business_card_text_extraction/openapi.json",
)

# Configure CORS (update for production to restrict origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FIXME: Set specific origins in production for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_text_with_gpt4(extracted_text, api_key):
    """Analyze text using GPT-4 to structure extracted information in JSON format."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = (
        f"Extract structured information from the following text in JSON format:\n"
        f"Text: {extracted_text}\n\n"
        "Output format:\n"
        "{\n"
        "  'data': {\n"
        "    'email': 'email@example.com',\n"
        "    'phone_numbers': ['+123456789', '+987654321'],\n"
        "    'agent_name': 'John Doe',\n"
        "    'company_name': 'Company Inc.',\n"
        "    'web_presence': {\n"
        "      'website': 'https://company.com',\n"
        "      'facebook': 'https://facebook.com/company',\n"
        "      'instagram': 'https://instagram.com/company',\n"
        "      'twitter': 'https://twitter.com/company'\n"
        "    }\n"
        "  }\n"
        "}\n"
        "If a field is not present, use null for that field."
    )

    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        completion = response.json()['choices'][0]['message']['content']
        try:
            # Parse the JSON response from the completion text
            return json.loads(completion)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response from GPT-4")
            raise HTTPException(status_code=500, detail="Failed to parse GPT-4 response")
    else:
        logger.error(f"OpenAI API request failed: {response.status_code} - {response.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch structured data from GPT-4")

@app.get("/")
async def read_root():
    """Root endpoint for basic API info."""
    return {"message": "Welcome to the Business Card Text Extraction API"}

@app.post("/api/business_card_text_extraction/extract_text")
async def extract_text(image: UploadFile = File(...)):
    """
    Extract text from an uploaded image file using OCR, then structure it to JSON format.
    """
    if image.content_type.split("/")[0] != "image":
        logger.error("Invalid file type uploaded")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")
    
    try:
        image_data = await image.read()
        logger.info("Image uploaded and read successfully")

        # Perform OCR to extract raw text from the image
        extracted_text = extract_text_from_image(image_data)
        logger.info("Text extracted successfully from the image")

        # Use GPT-4 API to restructure extracted text into JSON format
        restructured_text = analyze_text_with_gpt4(extracted_text, openai_api_key)

        logger.info("Text restructured using GPT-4 successfully")
        return JSONResponse(status_code=200, content={
            "message": "Text extracted and restructured successfully.",
            "extracted_text": extracted_text,
            "final_data": restructured_text
        })
    except Exception as e:
        logger.error(f"Failed to extract and structure text: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the image")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
