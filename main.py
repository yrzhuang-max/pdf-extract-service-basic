from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-text")
async def extract(file: UploadFile = File(...)):
    try:
        reader = PdfReader(file.file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        full_text = full_text.strip()
        if not full_text:
            return {"error": "no_text", "text": ""}
        # 只要成功拿到文字，就标记存在不可识别内容（pypdf无法区分哪些区域是图片，保守提示）
        return {
            "text": full_text,
            "has_unreadable_content": True
        }
    except Exception as e:
        return {"error": "parse_error", "msg": str(e)}
