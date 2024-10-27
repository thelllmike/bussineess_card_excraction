import os
import json
import base64
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("nvidia/Llama-3.1-Nemotron-70B-Instruct-HF")
# model = AutoModelForCausalLM.from_pretrained("nvidia/Llama-3.1-Nemotron-70B-Instruct-HF")

# def llama_create_json_from_text(extracted_text):
#     """Create JSON output from the extracted text using the LLAMA model."""

#     prompt = (
#         f"Extract the following information from this text and present it in JSON format with fields: "
#         f"email, phone_numbers, agent_name, company_name, web_presence (including website, facebook, instagram, twitter):\n\n"
#         f"Text: {extracted_text}\n\n"
#         f"Output format: {{ \"email\": \"\", \"phone_numbers\": [], \"agent_name\": \"\", \"company_name\": \"\", \"web_presence\": {{ \"website\": \"\", \"facebook\": \"\", \"instagram\": \"\", \"twitter\": \"\" }} }}\n\n"
#     )

#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(**inputs, max_length=512, num_return_sequences=1)
#     generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     try:
#         generated_json = json.loads(generated_text)
#     except json.JSONDecodeError:
#         raise ValueError("The model output could not be parsed as JSON.")
#     return generated_json


def analyze_image_and_append_recommendation_llm(image_bytes, api_key):
    """Analyze an image using GPT-4 to extract information in a structured format."""
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = """
    You are given an image of a business card or a similar document. Extract structured information from the image and provide the details in the following JSON format:
    {
        "data": {
            "email": "[Extracted email if present, otherwise null]",
            "phone_numbers": ["[List of extracted phone numbers]"],
            "agent_name": "[Extracted agent name or null]",
            "company_name": "[Extracted company name or null]",
            "web_presence": {
                "website": "[Extracted website URL if present, otherwise null]",
                "facebook": "[Extracted Facebook URL or handle, otherwise null]",
                "instagram": "[Extracted Instagram URL or handle, otherwise null]",
                "twitter": "[Extracted Twitter URL or handle, otherwise null]"
            }
        }
    }

    Analyze the content of the image carefully and extract any information that matches these fields. If some information is not present, use null for that field.
    """

    payload = {
        "model": "gpt-4o",  
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "image": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500  
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        completion = response.json()['choices'][0]['message']['content']
        return completion
    else:
        raise Exception(f"OpenAI API request failed: {response.status_code} - {response.text}")
