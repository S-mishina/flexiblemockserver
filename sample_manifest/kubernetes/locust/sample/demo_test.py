from locust import HttpUser, task
import time
class User(HttpUser):
    @task
    def get_employees(self) -> None:
        """Get a list of employees."""
        self.client.get("/")
        time.sleep(1)  # 1秒待機
