import re
import spacy
from paddleocr import PaddleOCR

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# Function to extract email addresses
def extract_email_ner(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_matches = re.findall(email_pattern, text)
    return list(set(email_matches))

# Function to extract phone numbers with refined patterns
def extract_phone_numbers_ner(text):
    # Updated regex pattern to capture:
    # 1. International numbers with + and area codes
    # 2. Numbers starting with 'n' or '0' and followed by 10 digits
    # 3. Multiple numbers separated by '/' (e.g., '0720953165/0733577492')
    phone_pattern = r'(\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,5}|\bn?\d{10}\b|\b0\d{9}\b(?:\/\d{10})?)'
    phone_matches = re.findall(phone_pattern, text)

    # Context-based filtering to prioritize valid phone numbers
    valid_phone_numbers = []
    for match in phone_matches:
        # Add numbers with or without keywords like 'Tel', 'Mobile', etc., if they meet length criteria
        if len(match) >= 7:
            # Check if the number is near relevant keywords for prioritization
            context_match = re.search(r'\b(Tel|Mobile|Phone|Contact|Cell)\b', text, re.IGNORECASE)
            if context_match or match.startswith(('+', 'n', '0')):
                valid_phone_numbers.append(match)
    
    return list(set(valid_phone_numbers))  # Deduplicate results


# Function to extract website URLs
def extract_website_ner(text):
    website_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    website_matches = re.findall(website_pattern, text)
    return list(set(website_matches))

# Function to extract agent and company names using NER with context filtering
def extract_entities_with_ner(text):
    doc = nlp(text)
    names = []
    organizations = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "ORG":
            organizations.append(ent.text)
    
    # Assuming the first name detected as "PERSON" is the agent
    agent_name = names[0] if names else None
    
    # Prioritize organizations with common company terms like "Division", "Office", "Ltd"
    company_name = None
    for org in organizations:
        if any(term in text for term in ["Division", "Office", "Ltd", "Corporation", "Inc", "Group", "Co"]):
            company_name = org
            break
    return agent_name, company_name

# Function to extract social media handles using regex
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

# Enhanced function to extract addresses
def extract_address_ner(text):
    # Refined regex pattern to capture address formats with terms like "Street", "Avenue", etc.
    address_pattern = (
        r'((?:\d{1,5}\s)?(?:[A-Za-z\s]+(?:Square|Building|Tower|Floor|Block|Avenue|St|Street|Rd|Road|Lane|Ln|Drive|Dr|Boulevard|Blvd|Place|Pl)[,.\s]*)+'
        r'(?:,\s*\w+)*,\s*\w+\s*\d{0,6}|\bP\.O\.\sBox\s\d+\b)'
    )
    address_matches = re.findall(address_pattern, text, re.IGNORECASE | re.MULTILINE)

    # spaCy NER for fallback location-based entities
    doc = nlp(text)
    additional_addresses = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC"}]

    # Combine regex and NER results to capture complete address
    addresses = list(set(address_matches + additional_addresses))
    # Filter out known country names if they appear at the end
    final_address = [addr for addr in addresses if addr.lower() not in {"kenya", "uganda", "tanzania"}]
    return ", ".join(final_address) if final_address else None

# OCR function to extract text from an image
def extract_text_from_image(image_bytes):
    ocr = PaddleOCR()
    result = ocr.ocr(image_bytes, cls=True)
    extracted_text = ""
    for idx in range(len(result)):
        for line in result[idx]:
            text, _ = line[-1]
            extracted_text += text + "\n"
    
    return extracted_text.strip()

# Function to restructure extracted text into JSON format
def restructure_extracted_text_to_json(extracted_text):
    """Restructure extracted text into JSON format for easy access to fields."""
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
