from pydantic import BaseModel

class LanguageRequest(BaseModel):
    selected_language: str