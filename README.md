# Chatbot Backend API

This is the backend API for a chatbot that processes user input and generates responses.

## Request Format

The API accepts requests in JSON format with the following structure:

{
    "message": "String",
    "model_id": "String" (one of: "meta-llama/Meta-Llama-3-8B-Instruct", "google/gemma-7b-it")
}

## Response Format

The API returns responses in JSON format with the following structure:

{
    "response": "String"
}

## Running the Application

To run the application, execute the following command:

export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000

