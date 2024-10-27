import re
import spacy
from paddleocr import PaddleOCR

nlp = spacy.load("en_core_web_sm")

def extract_email_ner(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_matches = re.findall(email_pattern, text)
    return list(set(email_matches))  

def extract_phone_numbers_ner(text):
    phone_pattern = r'(\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
    phone_matches = re.findall(phone_pattern, text)
    return list(set(phone_matches))  

def extract_website_ner(text):
    website_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    website_matches = re.findall(website_pattern, text)
    return list(set(website_matches))  

def extract_entities_with_ner(text):
    doc = nlp(text)

    agent_name = None
    company_name = None
    organizations = []
    names = []

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "ORG":
            organizations.append(ent.text)

    agent_name = names[0] if names else None
    company_name = organizations[0] if organizations else None
    return agent_name, company_name

def extract_social_media_ner(text):
    social_media = {
        "facebook": None,
        "instagram": None,
        "twitter": None
    }
    
    fb_pattern = r'(facebook\.com/[^\s]+|FB:[^\s]+|facebook.com|FB/|fb.com)'
    ig_pattern = r'(instagram\.com/[^\s]+|IG:[^\s]+|instagram.com|IG/|ig.com)'
    twitter_pattern = r'(twitter\.com/[^\s]+|Twitter:[^\s]+|twitter.com|Twitter/|t.co)'

    fb_match = re.findall(fb_pattern, text, re.IGNORECASE)
    ig_match = re.findall(ig_pattern, text, re.IGNORECASE)
    twitter_match = re.findall(twitter_pattern, text, re.IGNORECASE)
    
    social_media['facebook'] = fb_match[0] if fb_match else None
    social_media['instagram'] = ig_match[0] if ig_match else None
    social_media['twitter'] = twitter_match[0] if twitter_match else None

    return social_media

def extract_address_ner(text): 
    # extract address using regular expressions 
    address_pattern = r'(\d{1,4}\s\w+\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\,?\s?\w+?\s?\w+?,?\s?\d{5}|\bP\.O\.\sBox\s\d+\b)'
    address_matches = re.findall(address_pattern, text, re.IGNORECASE)

    # used spaCy's NER
    doc = nlp(text)
    additional_addresses = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    # Combining both regex and NER results
    addresses = list(set(address_matches + additional_addresses))

    return addresses[0] if addresses else None

def extract_text_from_image(image_bytes):
    """Extract text from an image using OCR."""
    ocr = PaddleOCR()
    result = ocr.ocr(image_bytes, cls=True)
    extracted_text = ""
    for idx in range(len(result)):
        for line in result[idx]:
            text, _ = line[-1]
            extracted_text += text + "\n"
    
    return extracted_text.strip()

def restructure_extracted_text_to_json(extracted_text):
    """Restructure extracted text to JSON. 
    
    This function uses re and spacy to extract entities from the text.
    Using re, it extracts email, phone numbers, website, and social media links.
    Using spacy's NER, it extracts agent name and company name.
    """
    email = extract_email_ner(extracted_text)
    phone_numbers = extract_phone_numbers_ner(extracted_text)
    website = extract_website_ner(extracted_text)
    social_media = extract_social_media_ner(extracted_text)
    agent_name, company_name = extract_entities_with_ner(extracted_text)
    address = extract_address_ner(extracted_text)

    return {
        "email": email[0] if email else None,
        "phone_numbers": phone_numbers[:2],  # Limit to only the first two phone numbers
        "agent_name": agent_name,
        "company_name": company_name,
        "address": address,
        "web_presence": {
            "website": website[0] if website else None,
            "facebook": social_media["facebook"],
            "instagram": social_media["instagram"],
            "twitter": social_media["twitter"]
        }
    }
