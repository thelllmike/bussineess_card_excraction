# Business Card Text Extraction API

## Overview
The **Business Card Text Extraction API** is a FastAPI service that extracts key information from images of business cards, including names, phone numbers, email addresses, company names, and web links. Using PaddleOCR for Optical Character Recognition (OCR) and spaCy for Natural Language Processing (NLP), this API processes the image and returns structured data in JSON format. Ideal for CRM integration, data entry automation, and lead management.

## Features
- **OCR-Based Text Extraction**: Extracts text from business card images with high accuracy.
- **Contact Info Parsing**: Identifies phone numbers, emails, names, and company names in various formats.
- **Social Media and Web Detection**: Extracts URLs for websites and social media profiles.
- **Structured Output**: Returns extracted information in a clean JSON format.

## Sample JSON Output
```json
{
  "email": "neha@aslcredit.co.ke",
  "phone_numbers": ["+254(20)2054138", "+254720585960"],
  "agent_name": "Neha Patel",
  "company_name": "Credit Limited",
  "address": "Eden Square, Westlands, Nairobi, Kenya",
  "web_presence": {
    "website": "www.aslcredit.co.ke",
    "facebook": null,
    "instagram": null,
    "twitter": null
  }
}
