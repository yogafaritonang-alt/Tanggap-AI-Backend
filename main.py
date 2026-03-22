import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = "AIzaSyDEgYie2sG8zDQN9vHisg4uZ6pAzHhr1pI" 

if not GEMINI_API_KEY:
    print("⚠️ PERINGATAN: Anda belum memasukkan Gemini API Key. Aplikasi akan error saat mencoba merespons.")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="Tanggap.AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_message: str
    bencana_konteks: str = "Gempa Bumi Magnitudo 5.2" 
    lokasi_user: str = "Jakarta Pusat"

SYSTEM_INSTRUCTION = """
Kamu adalah 'Tanggap.AI', asisten virtual darurat untuk mitigasi bencana di Indonesia.
Saat ini sedang terjadi peringatan: {bencana} di dekat lokasi pengguna: {lokasi}.

Tugasmu:
1. Jawab pertanyaan atau situasi pengguna dengan SANGAT SINGKAT dan TEGAS (maksimal 3-4 kalimat atau poin-poin).
2. Fokus pada TINDAKAN PENYELAMATAN NYAWA instan berdasarkan situasi yang mereka deskripsikan.
3. Jangan berikan pendahuluan atau penutup yang bertele-tele (misal: "Halo, saya turut prihatin..."). Langsung ke instruksi!
4. Gunakan tag HTML sederhana secara AMAN (seperti <b>, <strong>, <ul>, <li>, <ol>, <br>) untuk mempertegas instruksi agar mudah dibaca di aplikasi web.
5. Gunakan bahasa Indonesia yang mudah dipahami, jangan gunakan istilah teknis yang rumit.
6. Jika pengguna bertanya hal di luar mitigasi bencana, arahkan mereka kembali untuk fokus pada evakuasi dan keselamatan.
"""

@app.post("/api/chat")
async def get_ai_response(request: ChatRequest):
    try:
        contextual_prompt = SYSTEM_INSTRUCTION.format(
            bencana=request.bencana_konteks,
            lokasi=request.lokasi_user
        )
        
        full_prompt = f"{contextual_prompt}\n\nSituasi Pengguna: {request.user_message}\n\nBerikan instruksi darurat sekarang:"

        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=full_prompt
        )
        
        return {"response": response.text}

    except Exception as e:
        print(f"Error pada Gemini API: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal menghubungi server AI. Harap ikuti protokol standar: Jauhi bangunan, cari tempat lapang.")

@app.get("/")
def read_root():
    return {"status": "Tanggap.AI Backend is Running!", "version": "1.1 (Updated SDK)"}

if __name__ == "__main__":
    print("Memulai server FastAPI di http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)