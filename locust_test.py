from locust import HttpUser, task, between
import json



class MyUser(HttpUser):
    host = "http://178.63.193.205"
    wait_time = between(1, 2)



    @task
    def my_task(self):
        headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
        }
        payload = [
        {
        "query": "evaelfie",
        "since_time": 1702490520,
        "until_time": 1702490580
        }
        ]
        self.client.post("/search", data=json.dumps(payload), headers=headers)



# Configure the load test
if __name__ == "__main__":
    from locust.env import Environment
    from locust.log import setup_logging



    setup_logging("INFO", None)
    environment = Environment(user_classes=[MyUser])
    environment.create_local_runner()



    environment.create_web_ui("localhost", 8089)
    environment.runner.start(6, spawn_rate=1)
    environment.runner.greenlet.join()