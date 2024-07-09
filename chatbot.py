import torch
from transformers import AutoTokenizer, AutoModelForCausalLM,BitsAndBytesConfig, TextIteratorStreamer
import os
from threading import Thread
from google.cloud import secretmanager

class Chatbot:
    def __init__(self, 
                model_id,
                model_quantization_option,
                function_team = "IT",
                response_style = "concise and clear"
                ):
       self.get_huggingface_token()
       self.model_id = model_id
       self.quantization_config = set_quantization_config(model_quantization_option)
       self.torch_dtype = torch.bfloat16
       self.function_team = function_team
       self.response_style = response_style
       self.max_history_msgs = 5
       self.model = self.get_model()
       self.tokenizer = self.get_tokenizer()

    
    def get_huggingface_token(self):
        '''
        Function to get HF token
        '''
        # token_file_path = os.path.join(os.getenv("HOME"), ".cache", "huggingface", "token")
        # with open(token_file_path, "r") as f:
        #     hf_token = f.read().strip()
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/842140612422/secrets/huggingface/versions/latest"
        response = client.access_secret_version(request={"name": name})
        hf_token = response.payload.data.decode("UTF-8")
        print(hf_token)
        os.environ["HF_TOKEN"] = hf_token

    def get_system_prompt(self):
        '''
        Function to set system prompt
        '''
        team_msg = ''
        if self.function_team!="General":
            team_msg =  f'{self.function_team} team or '
        system_prompt = f'You are ECG AI, an intelligent assistant dedicated to providing {self.response_style} solutions for {team_msg}any general questions.  Analyze user queries and provide {self.response_style} answers. If user is asking question and you have no solution, politely ask clarifying questions but make it short. Please always reply in same language as the language of provided question.' # If user is not asking a question, introduce yourself and make your response limited to 2 sentences.
        return system_prompt

    def get_init_messages(self):
        '''
        Function to set system prompt into msgs
        '''
        init_msgs = []
        if self.model_id =="meta-llama/Meta-Llama-3-8B-Instruct":
            init_msgs.append({"role":"system","content":self.get_system_prompt()}) 
        else:
            init_msgs.append({"role":"user","content":self.get_system_prompt()}) 
            init_msgs.append({"role":"assistant","content":"Yes. Got it."}) # to follow user/assistant/ order
        return init_msgs
    
    def process_input_messages(self, messages):
        '''
        Function to add system msg to msgs and cut the length
        '''
        len_msg = len(messages)
        if len_msg>self.max_history_msgs:
            messages = messages[len_msg-self.max_history_msgs:]

        msgs = self.get_init_messages()

        for m in messages:
            msgs.append(m)

        return msgs

    def get_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.model_id,
                                                torch_dtype=self.torch_dtype,
                                                device_map="auto", 
                                                quantization_config=self.quantization_config)
        return model
    
    def get_tokenizer(self):
        return AutoTokenizer.from_pretrained(self.model_id, torch_dtype=self.torch_dtype)
    
    def response(self,messages):
        
        # set streamer
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        #add system msg to msgs and cut the length
        messages_ = self.process_input_messages(messages)
        
        # apply chat template
        messages_tmpl = self.tokenizer.apply_chat_template(messages_,
                               tokenize=False,
                               add_generation_prompt=True
                              )
        
        # tokenize msgs
        inputs = self.tokenizer([messages_tmpl], return_tensors="pt").to('cuda')
        
        # Run the generation in a separate thread, so that we can fetch the generated text in a non-blocking way.
        generation_kwargs = dict(inputs, 
                                 streamer=streamer, 
                                 max_new_tokens=1500,
                                 pad_token_id=self.tokenizer.eos_token_id)
        # chat
        thread = Thread(target=self.model.generate,
                        kwargs=generation_kwargs)
        thread.start() 
        
        for _, new_text in enumerate(streamer):
            yield new_text

    async def response_test(self,messages):
        
        # set streamer
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        #add system msg to msgs and cut the length
        messages_ = self.process_input_messages(messages)
        
        # apply chat template
        messages_tmpl = self.tokenizer.apply_chat_template(messages_,
                               tokenize=False,
                               add_generation_prompt=True
                              )
        
        # tokenize msgs
        inputs = self.tokenizer([messages_tmpl], return_tensors="pt").to('cuda')
        
        # Run the generation in a separate thread, so that we can fetch the generated text in a non-blocking way.
        generation_kwargs = dict(inputs, 
                                 streamer=streamer, 
                                 max_new_tokens=1500,
                                 pad_token_id=self.tokenizer.eos_token_id)
        # chat
        thread = Thread(target=self.model.generate,
                        kwargs=generation_kwargs)
        thread.start() 
        
        generated_text = ''
        for _, new_text in enumerate(streamer):
            generated_text += new_text
        return generated_text
            

def set_quantization_config(model_quantization_option):
    if model_quantization_option=="4bit":
        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
    else:
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    return quantization_config