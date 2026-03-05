from pydantic import BaseModel

class AskReq(BaseModel):
    question: str