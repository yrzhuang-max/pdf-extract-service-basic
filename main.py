from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pypdf
from io import BytesIO

app = FastAPI(title="PDF Extract Service")

# CORS，允许你的网站域名访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://filedocswift.com",
        "https://www.filedocswift.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SIZE = 20 * 1024 * 1024  # 20MB

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    # 校验后缀
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # 读取文件内容，同时校验大小
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large, max 20MB.")

    try:
        reader = pypdf.PdfReader(BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return {"text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
