from locust import HttpUser, task, between
import json
import random


class MyUser(HttpUser):
    host = "http://178.63.193.205"
    wait_time = between(2,3)

    @task
    def my_task(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = [
            {
                "query": "python",
                "since_time": random.randint(1702490520, 1702490580),
                "until_time": random.randint(1702490580, 1702490780),
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
    environment.runner.start(65, spawn_rate=1)
    environment.runner.greenlet.join()
