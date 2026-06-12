from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import os
import shutil

from ocr import extract_text_from_image
from gemini_extractor import extract_multiple_with_gemini
from extractor import extract_contact_details
from export_excel import save_cards_to_excel

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://cardflow.wecanserve.in"
# ],

#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
EXCEL_FILE = "exports/cardsdetails.xlsx"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("exports", exist_ok=True)


@app.get("/")
def home():
    return {"message": "OCR API Running"}


@app.post("/upload")
async def upload_cards(files: list[UploadFile] = File(...)):
    ocr_cards = []

    for index, file in enumerate(files, start=1):
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        raw_text = extract_text_from_image(file_path)

        print(f"========== CARD {index} RAW OCR TEXT ==========")
        print(raw_text)
        print("===============================================")

        ocr_cards.append({
            "card_no": index,
            "filename": file.filename,
            "raw_text": raw_text
        })

    try:
        results = extract_multiple_with_gemini(ocr_cards)

        for card in results:
            card["source"] = "gemini"

    except Exception as e:
        print("Gemini batch failed, using fallback extractor")
        print(e)

        results = []

        for card in ocr_cards:
            extracted_data = extract_contact_details(card["raw_text"])
            extracted_data["card_no"] = card["card_no"]
            extracted_data["source"] = "fallback"
            results.append(extracted_data)

    for card in results:
        matched = next(
            (item for item in ocr_cards if item["card_no"] == card["card_no"]),
            None
        )

        if matched:
            card["filename"] = matched["filename"]
            card["raw_text"] = matched["raw_text"]

    save_cards_to_excel(results)

    return {
        "total_cards": len(results),
        "cards": results,
        "excel_saved": True,
        "excel_file": EXCEL_FILE,
        "gemini_requests_used": 1
    }


@app.get("/download-excel")
def download_excel():
    if not os.path.exists(EXCEL_FILE):
        return {"message": "Excel file not found. Upload cards first."}

    return FileResponse(
        EXCEL_FILE,
        filename="cardsdetails.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )