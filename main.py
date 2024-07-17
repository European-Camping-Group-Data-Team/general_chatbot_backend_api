from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from chatbot import Chatbot
from typing import Dict
from uuid import uuid4
from datetime import datetime, timedelta
import time
import threading

# load model
model = Chatbot(model_id="meta-llama/Meta-Llama-3-8B-Instruct")

# Session setting

## In-memory storage for sessions
session_store: Dict[str, Dict] = {}

## Session timeout
SESSION_TIMEOUT = timedelta(minutes=30)
CLEANUP_INTERVAL = 3600  # Cleanup interval in seconds

# Data format
## ChatRequest     
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class User(BaseModel):
    user_id: str
        
## Response
class ChatResponse(BaseModel):
    user_id: str
    session_id:str
    response: str
        
app = FastAPI()

def create_session(user_id: str):
    session_id = str(uuid4())
    session_store[session_id] = {
        "user_id": user_id,
        "chat_history":[],
        "expires": datetime.now() + SESSION_TIMEOUT
    }
    return session_id

def get_session(session_id: str):
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    if session["expires"] < datetime.now():
        session_store.pop(session_id, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return session

def cleanup_sessions():
    while True:
        now = datetime.now()
        expired_sessions = [session_id for session_id, session in session_store.items() if session["expires"] < now]
        for session_id in expired_sessions:
            session_store.pop(session_id, None)
        time.sleep(CLEANUP_INTERVAL)

# Create and start the background thread of sessions management
cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
cleanup_thread.start()

@app.post("/chat")
async def chat(chat_request: ChatRequest): 
    try:
        user_id = chat_request.user_id
        session_id = chat_request.session_id
        message = chat_request.message
        
        current_session = get_session(session_id)
        
        # update expires time 
        current_session['expires'] = datetime.now() + SESSION_TIMEOUT
       
        # update session history 
        current_session["chat_history"].append({"role":"user","content":message})
        
        history = current_session["chat_history"]
        
        response =await model.response_test(history)
        
        current_session["chat_history"].append({"role":"assistant","content":message})
        
        chat_response = ChatResponse(user_id = user_id,session_id=session_id, response=response)
        
        return chat_response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{str(e)}")

@app.post("/new_session")
async def newSession(user:User):
    session_id = create_session(user.user_id)
    return session_id