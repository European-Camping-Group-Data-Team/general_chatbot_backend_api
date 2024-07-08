from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


from chatbot import Chatbot
import logging
import os
import datetime

# logging
log_file_name = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log'

if not os.path.exists(log_file_name):
    with open(log_file_name, 'w') as f:
        pass
    
logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# global var
nb_model_loaded = 0
nb_get_model = 0

# load model
model = Chatbot(model_id="meta-llama/Meta-Llama-3-8B-Instruct",
                       model_quantization_option="4bit",
                       function_team = "General",
                       response_style = "short and clear"
                       )
nb_model_loaded +=1
logging.info(f"Nb Model loaded : {nb_model_loaded}")

if nb_model_loaded>1:
    logging.error(f"Nb Model loaded : {nb_model_loaded}")
    
class ChatHistory(BaseModel):
    user_id: str
    history: list

class ChatResponse(BaseModel):
    user_id: str
    response: str
        
app = FastAPI()


@app.post("/chat")
async def chat(chathistory: ChatHistory):
    
    logging.info('chathistory: ', chathistory)
    try:
        history = chathistory.history
        user_id = chathistory.user_id
        
        response =await model.response_test(history)
        chatresponse = ChatResponse(user_id = user_id, response=response)
        logging.info('response',chatresponse)
        
        return chatresponse
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{str(e)}")