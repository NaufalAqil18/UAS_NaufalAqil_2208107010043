import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key dari .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("API key Gemini tidak ditemukan di .env")

# Konfigurasi Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Inisialisasi model Gemini
MODEL_NAME = "models/gemini-1.5-flash"  # atau gunakan "models/gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

# Inisialisasi FastAPI
app = FastAPI(title="Intelligent Email Writer API")

# Skema data permintaan pengguna
class EmailRequest(BaseModel):
    category: str
    recipient: str
    subject: str
    tone: str
    language: str
    urgency_level: Optional[str] = "Biasa"
    points: List[str]
    example_email: Optional[str] = None

# Fungsi untuk membentuk prompt teks dari input
def build_prompt(body: EmailRequest) -> str:
    lines = [
        f"Tolong buatkan email dalam bahasa {body.language.lower()} yang bernada {body.tone.lower()}",
        f"Ditujukan kepada: {body.recipient}.",
        f"Subjek email: {body.subject}.",
        f"Kategori: {body.category}.",
        f"Tingkat urgensi: {body.urgency_level}.",
        "",
        "Berikut adalah poin-poin yang harus dimuat dalam email:",
    ]
    for point in body.points:
        lines.append(f"- {point}")
    if body.example_email:
        lines += ["", "Sebagai referensi, berikut contoh email sebelumnya:", body.example_email]
    lines.append("")
    lines.append("Silakan buat email yang profesional, jelas, dan padat.")
    return "\n".join(lines)

# Endpoint untuk generate email
@app.post("/generate/")
async def generate_email(req: EmailRequest):
    prompt = build_prompt(req)

    try:
        # Kirim prompt ke Gemini API
        response = model.generate_content(prompt)

        # Ambil hasil teks dari response
        generated = response.text.strip()

        # Validasi hasil
        if not generated:
            raise HTTPException(status_code=500, detail="Tidak ada hasil dari Gemini API")

        return {"generated_email": generated}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")
