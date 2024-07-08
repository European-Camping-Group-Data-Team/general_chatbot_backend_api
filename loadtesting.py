from locust import HttpUser, TaskSet, task, between

chathistory = { 
'user_id': '123',
'history' :[{'role': 'user', 'content': "how can i use locust to test my fastapi app"}]  
}



class UserBehavior(TaskSet):
    @task(1)
    def chat(self):
        self.client.post("/chat", json=chathistory)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    min_wait=5 #interval time between questions posted by same user
    max_wait=120 
    host = "http://localhost:8503"