from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pypdf
from io import BytesIO
import re

app = FastAPI(title="PDF Extract Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://filedocswift.com",
        "https://www.filedocswift.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large, max 10MB.")

    try:
        reader = pypdf.PdfReader(BytesIO(content))
        text = ""
        has_text_page = False
        has_non_text_page = False

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
                has_text_page = True
            else:
                has_non_text_page = True

        if not has_text_page:
            doc_type = "image-only"
        elif has_text_page and has_non_text_page:
            doc_type = "mixed"
        else:
            doc_type = "normal"

        text = text.strip()
        # 过滤不可打印控制字符，重点清除换页符 \f(\x0c)，保留换行\n、制表\t
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1F]', '', text)

        return {
            "text": text,
            "type": doc_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
