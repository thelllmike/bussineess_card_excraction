import re
import spacy
from paddleocr import PaddleOCR
from geotext import GeoText

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# -----------------------------------------------------------------------------
# 1. Function to extract email addresses
# -----------------------------------------------------------------------------
def extract_email_ner(text):
    """
    Extracts email addresses using regex.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_matches = re.findall(email_pattern, text)
    return list(set(email_matches))  # Return unique matches

# -----------------------------------------------------------------------------
# 2. Function to extract phone numbers with refined patterns
# -----------------------------------------------------------------------------
def extract_phone_numbers_ner(text):
    """
    Extracts phone numbers with patterns to handle:
      - International numbers with + and area codes
      - Numbers starting with 'n' or '0' and followed by 10 digits
      - Multiple numbers separated by '/' (e.g., '0720953165/0733577492')
    Also includes basic context-based filtering.
    """
    phone_pattern = (
        r'(\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,5}'
        r'|\bn?\d{10}\b|\b0\d{9}\b(?:/\d{10})?)'
    )
    phone_matches = re.findall(phone_pattern, text)

    valid_phone_numbers = []
    for match in phone_matches:
        if len(match) >= 7:
            # Check for "Tel", "Mobile", etc. or if number starts with +, n, 0
            context_match = re.search(r'\b(Tel|Mobile|Phone|Contact|Cell)\b', text, re.IGNORECASE)
            if context_match or match.startswith(('+', 'n', '0')):
                valid_phone_numbers.append(match)

    return list(set(valid_phone_numbers))  # Deduplicate results

# -----------------------------------------------------------------------------
# 3. Function to extract website URLs
# -----------------------------------------------------------------------------
def extract_website_ner(text):
    """
    Extracts website URLs via regex pattern.
    """
    website_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    website_matches = re.findall(website_pattern, text)
    return list(set(website_matches))

# -----------------------------------------------------------------------------
# 4. Function to extract agent and company names using NER with context filtering
# -----------------------------------------------------------------------------
def extract_entities_with_ner(text):
    """
    Uses spaCy Named Entity Recognition (NER) to extract 'PERSON' and 'ORG' entities.
    Returns a tuple (agent_name, company_name).
    """
    doc = nlp(text)
    names = []
    organizations = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "ORG":
            organizations.append(ent.text)
    
    # Assume the first PERSON is the agent name
    agent_name = names[0] if names else None
    # Assume the first ORG is the company name
    company_name = organizations[0] if organizations else None

    return agent_name, company_name

# -----------------------------------------------------------------------------
# 5. Function to extract social media handles using regex (optional)
# -----------------------------------------------------------------------------
def extract_social_media_ner(text):
    """
    Extracts basic references to Facebook, Instagram, and Twitter from text via regex.
    Returns a dictionary with any matched snippet or None if not found.
    """
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

# -----------------------------------------------------------------------------
# 6. Enhanced function to extract addresses
# -----------------------------------------------------------------------------
def extract_address_ner(text):
    """
    Extract potential address formats that contain typical address keywords 
    like 'Street', 'Avenue', 'Building', etc. Also uses spaCy NER to catch
    GPE/LOC/FAC as fallback for location phrases.
    """
    address_pattern = (
        r'((?:\d{1,5}\s)?'
        r'(?:[A-Za-z\s]+(?:Square|Building|Tower|Floor|Block|Avenue|St|Street|'
        r'Rd|Road|Lane|Ln|Drive|Dr|Boulevard|Blvd|Place|Pl)[,.\s]*)+'
        r'(?:,\s*\w+)*'
        r',\s*\w+\s*\d{0,6}'
        r'|\bP\.O\.\sBox\s\d+\b)'
    )
    address_matches = re.findall(address_pattern, text, re.IGNORECASE | re.MULTILINE)

    # Use spaCy to capture additional location-based entities
    doc = nlp(text)
    additional_addresses = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC"}]

    # Combine regex and NER results
    addresses = list(set(address_matches + additional_addresses))

    # Filter out known country names if they appear as isolated addresses 
    # (Modify this set to match your usage.)
    final_address = [addr for addr in addresses if addr.lower() not in {"kenya", "uganda", "tanzania"}]
    
    return ", ".join(final_address) if final_address else None

# -----------------------------------------------------------------------------
# 7. OCR function to extract text from an image
# -----------------------------------------------------------------------------
def extract_text_from_image(image_bytes):
    """
    Uses PaddleOCR to extract text from an image given as bytes.
    """
    ocr = PaddleOCR()
    result = ocr.ocr(image_bytes, cls=True)
    extracted_text = ""
    for idx in range(len(result)):
        for line in result[idx]:
            text, _ = line[-1]
            extracted_text += text + "\n"
    
    return extracted_text.strip()

# -----------------------------------------------------------------------------
# 8. Final function to restructure extracted text into the requested JSON format
#    using GeoText to detect city and country.
# -----------------------------------------------------------------------------
def restructure_extracted_text_to_json(extracted_text):
    """
    Restructure extracted text into a JSON/dictionary with specific fields:
      - organization_name
      - primary_phone_number
      - other_phone_number
      - email
      - industry
      - city
      - country
      - website
    """
    # 1. Extract data using the helper functions
    emails = extract_email_ner(extracted_text)
    phone_numbers = extract_phone_numbers_ner(extracted_text)
    websites = extract_website_ner(extracted_text)
    agent_name, company_name = extract_entities_with_ner(extracted_text)
    address = extract_address_ner(extracted_text)

    # 2. Detect city/country using GeoText
    places = GeoText(extracted_text)
    # The library returns sets, but let's just pick the first city/country if available.
    # If there are multiple, you can decide how to handle them (e.g., store them in a list).
    city = list(places.cities)[0] if places.cities else None
    country = list(places.countries)[0] if places.countries else None

    # 3. Naive placeholder for industry
    industry = None

    # 4. Build and return the final dictionary
    return {
        "organization_name": company_name,
        "primary_phone_number": phone_numbers[0] if phone_numbers else None,
        "other_phone_number": phone_numbers[1] if len(phone_numbers) > 1 else None,
        "email": emails[0] if emails else None,
        "industry": industry,
        "city": city,
        "country": country,
        "website": websites[0] if websites else None
    }

# -----------------------------------------------------------------------------
# Usage Example (for reference):
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sample_text = """
        ABC Corporation Ltd
        Tel: +1 234 567 8900
        Cell: 0720953165
        Email: info@abccorp.com
        Website: www.abccorp.com
        1234 Some Avenue, Nairobi, Kenya
        Then we traveled to Mombasa in Kenya. 
    """
    
    # Extract data from the sample text
    structured_data = restructure_extracted_text_to_json(sample_text)
    print(structured_data)
