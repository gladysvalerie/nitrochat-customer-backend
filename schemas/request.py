from pydantic import BaseModel

class AskReq(BaseModel):
    question: str
    thread_id: str