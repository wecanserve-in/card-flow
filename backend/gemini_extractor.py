import os
import json
import mimetypes

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

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
        "card_no",
        "name",
        "company",
        "designation",
        "phone",
        "country",
        "email",
        "website",
        "address"
    ]
}

BATCH_SCHEMA = {
    "type": "array",
    "items": CARD_SCHEMA
}


def extract_multiple_with_gemini(image_cards):
    contents = []

    prompt = """
You will receive multiple business card images.

Extract details from EVERY image.

Return ONLY a valid JSON array.

Rules:
- First image = card_no 1
- Second image = card_no 2
- Continue sequentially.
- Never skip an image.
- If field missing return "Not available".
- Do not invent values.
- Extract:
name
company
designation
phone
country
email
website
address
"""

    contents.append(types.Part.from_text(text=prompt))

    for card in image_cards:
        mime_type = mimetypes.guess_type(card["file_path"])[0] or "image/jpeg"

        with open(card["file_path"], "rb") as f:
            image_bytes = f.read()

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=2000,
            response_mime_type="application/json",
            response_schema=BATCH_SCHEMA
        )
    )

    data = json.loads(response.text)

    for item in data:
        for key in CARD_SCHEMA["properties"]:
            if not item.get(key):
                item[key] = "Not available"

    return data