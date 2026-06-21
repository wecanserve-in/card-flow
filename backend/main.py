from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import os
import shutil

from gemini_extractor import extract_multiple_with_gemini
from export_excel import save_cards_to_excel

app = FastAPI()

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
    return {"message": "Gemini Card Extraction API Running"}


@app.post("/upload")
async def upload_cards(files: list[UploadFile] = File(...)):
    if len(files) > 10:
        return {"message": "Maximum 10 cards allowed per upload."}

    image_cards = []

    for index, file in enumerate(files, start=1):
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_cards.append({
            "card_no": index,
            "filename": file.filename,
            "file_path": file_path
        })

    try:
        results = extract_multiple_with_gemini(image_cards)

        for card in results:
            card["source"] = "gemini"

    except Exception as e:
        return {"error": str(e)}

    for card in results:
        matched = next(
            (
                item for item in image_cards
                if item["card_no"] == card["card_no"]
            ),
            None
        )

        if matched:
            card["filename"] = matched["filename"]

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