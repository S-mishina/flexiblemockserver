import unittest
from project.main import app
import os

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.test_yaml_file_path = 'test/config/custom_rule.yaml'
        os.environ['CUSTOM_RULE_YAML_FILE'] = self.test_yaml_file_path

    def tearDown(self):
        if 'CUSTOM_RULE_YAML_FILE' in os.environ:
            del os.environ['CUSTOM_RULE_YAML_FILE']

    def test_top_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['top'], 'Hello mock server')

    def test_index_route(self):
        response = self.app.get('/5/200')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['sleep_time'], 5)
        self.assertEqual(response.json['status_code'], 200)

    def test_index_route_1(self):
        response = self.app.get('/5/200/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['sleep_time'], 5)
        self.assertEqual(response.json['status_code'], 200)

    def test_only_sleep_time_route(self):
        response = self.app.get('/sleep/3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['sleep_time'], 3)
        self.assertEqual(response.json['status_code'], 200)

    def test_only_sleep_time_route_1(self):
        response = self.app.get('/sleep/3/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['sleep_time'], 3)
        self.assertEqual(response.json['status_code'], 200)

    def test_only_status_code_route(self):
        response = self.app.get('/status/404')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['status_code'], 404)

    def test_only_status_code_route(self):
        response = self.app.get('/status/404/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['status_code'], 404)

    def test_index_query_route(self):
        response = self.app.get('/10/201/query?param1=value1&param2=value2')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['sleep_time'], 10)
        self.assertEqual(response.json['status_code'], 201)
        self.assertEqual(response.json['output'], "{'param1': 'value1', 'param2': 'value2'}")

    def test_only_sleep_time_query_route(self):
        response = self.app.get('/sleep/2/query?param1=value1&param2=value2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['sleep_time'], 2)
        self.assertEqual(response.json['status_code'], 200)
        self.assertEqual(response.json['output'], "{'param1': 'value1', 'param2': 'value2'}")

    def test_only_status_code_query_route(self):
        response = self.app.get('/status/500/query?param1=value1&param2=value2')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status_code'], 500)
        self.assertEqual(response.json['output'], "{'param1': 'value1', 'param2': 'value2'}")

    def test_new_route(self):
        response = self.app.get('/new')
        self.assertEqual(response.status_code, 500)

    def test_new_route(self):
        response = self.app.get('/example')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, '{"message":"Example response"}')
