from pydantic import BaseModel

class PDFRequest(BaseModel):
    pdf_base64: str

class CheckInput(BaseModel):
    token: str
    qrraw: str