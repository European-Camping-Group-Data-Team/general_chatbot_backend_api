# Chatbot Backend API

This is the backend API for a chatbot that processes user input and generates responses.

A new chat process begins from creating a new session then post question with session id.

# 1. Get Session id

URL = "http://34.78.108.153:8503/new_session"

- Request Format

The API accepts requests in JSON format with the following structure:

{
   
    "user_id": String
}

- Response Format

The API returns responses in JSON format with the following structure:

{
    "session_id": String
}

# 2. Chat 

URL = "http://34.78.108.153:8503/chat"

- Request Format

The API accepts requests in JSON format with the following structure:

{
   
    "user_id": String",
    "session_id": String,
    "message": String
}

- Response Format

The API returns responses in JSON format with the following structure:

{
   
    "user_id": String",
    "session_id": String,
    "response": String
}

## Running the Application Using pm2
- install pm2: $npm install pm2
- run: $pm2 start "uvicorn main:app --host 0.0.0.0 --port 8503" --name chatbot_backend
- check logs: $pm2 logs chatbot_backend
- stop: $pm2 stop chatbot_backend

## Load testing
- #locust -f loadtesting.py 

## Curl through external ip
curl -X POST \
  http://34.78.108.153:8502/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Tell me a joke?",
           "model_id":"google/gemma-7b-it"   
}'