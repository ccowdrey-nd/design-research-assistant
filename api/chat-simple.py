from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Design & Research Assistant API"}

@app.post("/", response_model=ChatResponse)
async def chat_simple(chat_message: ChatMessage):
    """Simple chat endpoint"""
    return ChatResponse(
        response="I'm the Design & Research Assistant! I can help you search Figma files and export assets. What would you like to do?"
    )
