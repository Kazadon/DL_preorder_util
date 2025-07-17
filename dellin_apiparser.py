import requests
import json
from dotenv import dotenv_values
# Переписать в ООП, добавить методы - авторизация, проверка сессии, вывод списка заказов на определенную дату от Гермеон, печать предварительных заявок


class DellinScraper:

    def __init__(self, token: str, login: str, password: str):
        self.headers = {'accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.login = login
        self.password = password
        self.token = token
        self.sessionID = None
    
    # Аутентификация, получение sessionID для дальнейшей работы
    def auth(self) -> None:
        url = 'https://api.dellin.ru/v3/auth/login.json'
        data = {"appkey": self.token,
                "login": self.login,
                "password": self.password}
        json_string = json.dumps(data)
        response = requests.post(url, headers=self.headers, data=json_string)
        if response.status_code == 200:
            print(f"\nResponse 200.\nAUTH - succesful request\n{response.text}")
            self.sessionID = json.loads(response.content)['data']['sessionID']

        else:
            print("\nAUTH ERROR")
            print(response)

    # Проверка активности сессии
    def check_session(self) -> None:
        url = 'https://api.dellin.ru/v3/auth/session_info.json'
        data = {"appKey": self.token,
                "sessionID": self.sessionID}
        json_string = json.dumps(data)
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            print(f"\nResponse 200.\nCheck session - succesful request.\nsessionID: {data['sessionID']}\n{response.text}")
        else:
            print("\nCHECK SESSION ERROR \nWrong ApiToken/sessionID or something went wrong\nTry again to auth")
            print(response)

    def close_session(self) -> None:
        url = 'https://api.dellin.ru/v3/auth/logout.json'
        data = {"appKey": self.token,
                "sessionID": self.sessionID}
        json_string = json.dumps(data)
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            print(f"\nResponse 200.\nLOGOUT - succesful request.\nSESSION CLOSED\n{response.text}")
        else:
            print("\nCLOSE SESSION ERROR\nWrong ApiToken/sessionID or something went wrong\nTry again")
            print(response)

    def order_list(self) -> None:
        # 'https://api.dellin.ru/v3/orders.json'
        pass

    def documents_list(self) -> None:
        # 'https://api.dellin.ru/v1/customers/request/pdf.json'
        pass

config = dotenv_values('.env')
app = DellinScraper(config['DL_API_TOKEN'], config['LOGIN'], config['PASSWORD'])
app.auth()
app.check_session()


app.close_session()