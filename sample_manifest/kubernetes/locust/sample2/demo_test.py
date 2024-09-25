from locust import HttpUser, task

class User(HttpUser):
    @task 
    def get_employees(self) -> None:
        """Get a list of employees."""
        self.client.get("/")
        self.client.get("/status/500")
