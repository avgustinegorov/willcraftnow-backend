import json
import logging
import random

from locust import *

USED_USER_CREDENTIALS = []
ACTIVE_USER_CREDENTIALS = {"password": None, "email": None}


class UserTasks(SequentialTaskSet):

    def on_start(self):
        self.email = "chingkh@hotmail.com"
        self.password = "mostafa123"
        r = self.client.get("/adminconfig/")

        if r.status_code is not 200:
            raise Exception("Config Failed", r.content)

        self.client_id = json.loads(r.content)['client_id']

        self.oAuthParams = {
            "client_id": self.client_id,
            "grant_type": 'password'
        }

        logging.info('Client ID: %s',
                     self.client_id)

    # @task
    # def login_or_register(self):
    #     r = self.client.post('/auth/is_user/', {"email": self.email})
    #     if json.loads(r.content)['status'] == "Not Registered":
    #         self.register()
    #     else:
    #         self.login()

    @task
    def login(self):
        r = self.client.options('/auth/is_user/')
        params = {
            'email': self.email,
            'password': self.password,
            **self.oAuthParams
        }
        url = f"/auth/login/"
        r = self.client.post(url, data=params)
        logging.info('Login with %s email and %s password',
                     self.email, self.password)
        logging.info(f'login {r.status_code}')
        self.access_token = json.loads(r.content)['access_token']

    # def register(self):
    #     params = {
    #         'email': self.email,
    #         'password': self.password,
    #         'repeat_password': self.password,
    #         **self.oAuthParams
    #     }
    #     url = f"/auth/register/"
    #     r = self.client.post(url, data=params)
    #     logging.info('Register with %s email and %s password',
    #                  self.email, self.password)
    #     logging.info(f'register {r.status_code}')
    #     self.access_token = json.loads(r.content)['access_token']

    @task
    def set_order_details(self):
        url = f"/order/{613}/"
        r = self.client.get(
            url, headers={"authorization": "Bearer " + self.access_token}, )
        logging.info(f'set_order_details {r.status_code}')
        assert type(json.loads(r.content)) == dict
        self.order_details = json.loads(r.content)

    # @task
    # def list_orders(self):
    #     url = f"/order/list/"
    #     r = self.client.get(
    #         url, headers={"authorization": "Bearer " + self.access_token}, )
    #     logging.info(f'list_orders {r.status_code}')
    #     assert type(json.loads(r.content)) == list
    #     self.orders = json.loads(r.content)

    # @task
    # def update_user_details(self):
    #     params = {
    #         "id": "", "user_type": "", "name": "mostfa", "id_number": "karimi", "id_document": "Passport",
    #         "country_of_issue": "AO", "date_of_birth": "2018-3-3", "address": "", "real_estate_type": "HDB_EC",
    #         "block_number": "21", "floor_number": "21", "unit_number": "21", "street_name": "784", "country": "AX",
    #         "postal_code": "6454", "religion": "Christianity", "citizenship_status": "Foreigner",
    #         "relationship_status": "Single", "underage_children": "No", "gender": "Male",
    #         "contact_number": "+65 5556-4646", "display_name": "", "referring_partners": "", "labels": ""
    #     }
    #     url = f"/auth/user/"
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'update_user_details {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #
    # @task
    # def create_update_order(self):
    #     if self.orders:
    #         self.current_order = self.orders[0]
    #     else:
    #         self.current_order = self.create_order()
    #
    # def create_order(self):
    #     params = {
    #         "order_type": "WILL", "has_prior_will": False,
    #         "tncs": False, "disclaimer": False
    #     }
    #     url = f"/order/create/WILL/"
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_order {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     return json.loads(r.content)
    #
    # def set_order_details(self):
    #     url = f"/order/{self.current_order['id']}/"
    #     r = self.client.get(
    #         url, headers={"authorization": "Bearer " + self.access_token}, )
    #     logging.info(f'set_order_details {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.order_details = json.loads(r.content)

    # @task
    # def get_current_order_details(self):
    #     self.set_order_details()
    #
    # def create_charity(self):
    #     params = {"id": "", "name": "df", "UEN": "2323",
    #               "display_name": "", "labels": ""}
    #     url = f"/order/{self.current_order['id']}/charity/"
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_charity {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.set_order_details()
    #     return json.loads(r.content)
    #
    # def create_person(self):
    #     params = {
    #         "id": "", "name": "kdf", "id_number": "123", "id_document": "Passport", "country_of_issue": "AX",
    #         "date_of_birth": "1957-5-5", "address": "", "block_only_address": "", "real_estate_type": "HDB_FLAT",
    #         "block_number": "12", "floor_number": "3", "unit_number": "34", "street_name": "afa", "country": "AX",
    #         "postal_code": "3423", "religion": "Buddhism", "citizenship_status": "Singapore Permanent Resident",
    #         "gender": "Male", "relationship": "Brother", "contact_number": "+65 4444-4444", "email": "kj@ifnoei.idfjo",
    #         "display_name": "", "is_private_housing": "", "labels": ""
    #     }
    #     url = f"/order/{self.current_order['id']}/person/"
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_person {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.set_order_details()
    #     return json.loads(r.content)
    #
    # def set_entities(self):
    #     url = f"/order/{self.current_order['id']}/assets/{self.order_details['assets'][0]['id']}/allocations/"
    #     r = self.client.options(
    #         url, headers={"authorization": "Bearer " + self.access_token}, )
    #     logging.info(f'set_entities {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.entities = json.loads(
    #         r.content)['actions']['PUT']['entity']['choices']
    #
    # @task
    # def create_ten_persons_charities(self):
    #     self.set_entities()
    #     for i in range(len(self.entities), 10):
    #         if i % 2 == 0:
    #             self.create_person()
    #         else:
    #             self.create_charity()
    #
    # @task
    # def set_all_entities(self):
    #     self.set_entities()
    #     self.set_order_details()
    #
    # def create_residual_allocation(self, entity):
    #     params = {
    #         "asset_store": self.order_details['assets'][0]['id'],
    #         "entity": entity['value'],
    #         "allocation_percentage": "10",
    #         "effective_allocation_percentage": "",
    #         "effective_allocation_amount": "",
    #         "labels": ""
    #     }
    #     url = f"/order/{self.current_order['id']}/assets/{self.order_details['assets'][0]['id']}/allocations/"
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_residual_allocation {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.set_order_details()
    #
    # @task
    # def create_ten_residual_allocations(self):
    #     residual_asset = None
    #     for asset in self.order_details['assets']:
    #         if asset['asset_type'] == 'Residual':
    #             residual_asset = asset
    #             break
    #
    #     for i in range(len(residual_asset['entities']), 10):
    #         self.create_residual_allocation(self.entities[i])
    #
    # def create_asset(self, asset_type, params):
    #     # first call an options request
    #     url = f"/order/{self.current_order['id']}/assets/{asset_type}/"
    #     r = self.client.options(
    #         url, headers={"authorization": "Bearer " + self.access_token}, )
    #     assert type(json.loads(r.content)) == dict
    #
    #     # create asset
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_asset {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.set_order_details()
    #
    # def create_real_estate_asset(self):
    #     self.create_asset(
    #         'RealEstate', {
    #             "id": "", "real_estate_type": "HDB_EC", "block_number": "21", "floor_number": "34", "unit_number": "23",
    #             "street_name": "21", "country": "SG", "postal_code": "339696", "mortgage": "NO_MORTGAGE", "address": "",
    #             "holding_type": "SOLE_OWNER", "labels": ""
    #         }
    #     )
    #
    # def create_bank_account_asset(self):
    #     self.create_asset(
    #         'BankAccount', {
    #             "id": "", "created_at": "", "last_updated_at": "",
    #             "bank": "salkdfj", "account_number": "12",
    #             "holding_type": "INDIVIDUALLY", "labels": ""
    #         }
    #     )
    #
    # def create_insurance_asset(self):
    #     self.create_asset(
    #         'Insurance', {
    #             "id": "", "created_at": "", "last_updated_at": "",
    #             "insurer": "kljlj", "plan": "slafk",
    #             "policy_number": "2132", "has_existing_nomination": "NO", "labels": ""
    #         }
    #     )
    #
    # def create_investment_account_asset(self):
    #     self.create_asset(
    #         'Investment', {
    #             "id": "", "created_at": "", "last_updated_at": "", "financial_institution": "safsa",
    #             "account_number": "231", "holding_type": "INDIVIDUALLY", "labels": ""
    #         }
    #     )
    #
    # def create_company_asset(self):
    #     self.create_asset(
    #         'Company', {
    #             "id": "", "created_at": "", "last_updated_at": "", "name": "qqqqqqqu",
    #             "registration_number": "23123", "incorporated_in": "SG", "shares_amount": "21",
    #             "percentage": "23", "labels": ""
    #         }
    #     )
    #
    # @task
    # def create_ten_assets(self):
    #     self.set_order_details()
    #
    #     # first asset is residual asset!
    #     asset_creators = [
    #         self.create_real_estate_asset,
    #         self.create_bank_account_asset,
    #         self.create_insurance_asset,
    #         self.create_investment_account_asset,
    #         self.create_company_asset
    #     ]
    #     for i in range(len(self.order_details['assets']), 11):
    #         asset_creators[i % len(asset_creators)]()
    #
    # def create_appointment(self, appointment_type):
    #     # first call an options request
    #     url = f"/order/{self.current_order['id']}/appointments/"
    #     r = self.client.options(
    #         url, headers={"authorization": "Bearer " + self.access_token}, )
    #     assert type(json.loads(r.content)) == dict
    #
    #     # create appointment
    #     person = self.create_person()
    #     params = {"updated_type": appointment_type,
    #               "person": person['id'], "labels": ""}
    #     r = self.client.post(url, data=params, headers={
    #                          "authorization": "Bearer " + self.access_token})
    #     logging.info(f'create_appointment {r.status_code}')
    #     assert type(json.loads(r.content)) == dict
    #     self.set_order_details()
    #
    # def get_number_of_people_of_type(self, people_type):
    #     cnt = 0
    #     for people in self.order_details['people']:
    #         if people_type in people['entity_roles']:
    #             cnt += 1
    #     return cnt
    #
    # @task
    # def create_appointment_executor(self):
    #     if self.get_number_of_people_of_type('EXECUTOR') == 0:
    #         self.create_appointment('EXECUTOR')
    #
    # @task
    # def create_appointment_witness(self):
    #     for i in range(0, 2):
    #         if self.get_number_of_people_of_type("WITNESS") < 2:
    #             self.create_appointment("WITNESS")
    #
    # @task
    # def get_summary(self):
    #     url = f"/order/{self.current_order['id']}/"
    #     r = self.client.get(
    #         url, headers={"authorization": "Bearer " + self.access_token})
    #     logging.info(f'get_summary {r.status_code}')
    #     assert type(json.loads(r.content)) == dict


class LoadTest(HttpUser):
    tasks = [UserTasks]
    host = "http://localhost:8000"
    sock = None
    wait_time = between(3, 5)

    def __init__(self, env):
        super().__init__(env)
        global USED_USER_CREDENTIALS
        global ACTIVE_USER_CREDENTIALS
        username = f"testuser_{random.randint(100, 300)}"
        while username in USED_USER_CREDENTIALS:
            username = f"testuser_{random.randint(100, 300)}"
        USED_USER_CREDENTIALS.append(username)
        ACTIVE_USER_CREDENTIALS["email"] = f"{username}@email.com"
        ACTIVE_USER_CREDENTIALS["password"] = f"password{username}"
