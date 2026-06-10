import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "card_no": {"type": "integer"},
        "name": {"type": "string"},
        "company": {"type": "string"},
        "designation": {"type": "string"},
        "phone": {"type": "string"},
        "country": {"type": "string"},
        "email": {"type": "string"},
        "website": {"type": "string"},
        "address": {"type": "string"}
    },
    "required": [
        "card_no", "name", "company", "designation",
        "phone", "country", "email", "website", "address"
    ]
}

BATCH_SCHEMA = {
    "type": "array",
    "items": CARD_SCHEMA
}


def extract_multiple_with_gemini(ocr_cards):
    cards_text = ""

    for card in ocr_cards:
        cards_text += f"""
CARD {card["card_no"]}:
{card["raw_text"]}

---
"""

    prompt = f"""
Extract business card details from OCR text.

Return only JSON array.

Rules:
- Each card must be separate.
- Preserve card_no exactly.
- If missing, use "Not available".
- Fix obvious OCR mistakes:
  gmail com -> gmail.com
  condotsystems com -> condotsystems.com
  WWWE -> www
- Join split company names.
- Join split phone numbers.
- Do not invent missing values.
- Keep address complete but clean.

OCR CARDS:
{cards_text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=900,
            response_mime_type="application/json",
            response_schema=BATCH_SCHEMA
        )
    )

    print("========== GEMINI BATCH RESPONSE ==========")
    print(response.text)
    print("===========================================")

    data = json.loads(response.text)

    for item in data:
        for key in CARD_SCHEMA["properties"].keys():
            if not item.get(key):
                item[key] = "Not available"

    return data