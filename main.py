from flask import Flask, request, jsonify, session
from flask_session import Session
from chatbot import Chatbot
import logging

# logging
logging.basicConfig(filename='logs/{datetime.date.today().isoformat()}.log', level=logging.DEBUG)

# app config
app = Flask(__name__)
app.config['SECRET_KEY'] = '819428'  # Change this to a secure random key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# global var
nb_model_loaded = 0
nb_get_model = 0

# load model
model_llamma = Chatbot(model_id="meta-llama/Meta-Llama-3-8B-Instruct",
                       model_quantization_option="4bit",
                       function_team = "General",
                       response_style = "short and clear"
                       )
nb_model_loaded +=1
logging.info(f"Nb Model loaded : {nb_model_loaded}")

# model_gemma = ChatbotModel(model_id="google/gemma-7b-it")

def get_model(model_id):
    # if model_id == "google/gemma-7b-it":
    #     return model_gemma
    # else:
    #     return model_llamma
    
    global nb_get_model
    nb_get_model +=1
    logging.info(f"Nb Get Model : {nb_get_model}")
    
    return model_llamma
    
@app.route('/chat', methods=['POST'])
def chat():
    try:
        logging.info(f'Get request: {request.json}')
        user_message = request.json['message']
        model_id = request.json['model_id']
        
        # Initialize chat history for the user if it doesn't exist
        if 'chat_history' not in session:
            session['chat_history'] = []
            session['model_id'] = model_id
        
        # when user changes model, clear memory
        if session['model_id']!=model_id:
            session['chat_history'] = []
            session['model_id'] = model_id
        
        # Add user message to chat history
        session['chat_history'].append({'role': 'user', 'content': user_message})
        
        # Generate response using the entire chat history
        model = get_model(session['model_id'])
        response = model.response_test(session['chat_history'])
        
        # Add AI response to chat history
        session['chat_history'].append({'role': 'assistant', 'content': response})
        
        # Save the session
        session.modified = True
        logging.info()
        
        return jsonify({'response': response})
    except KeyError as e:
        return jsonify({'response': 'Invalid request, "message" key is missing'}), 400
    except Exception as e:
        return jsonify({'response': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8502)

