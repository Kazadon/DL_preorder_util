import requests
import json
from dotenv import dotenv_values
import os
import base64
from printdocs import PrintDocument
# import win32print
# import win32api


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
            print(f"\nAUTH - succesful request\n")
            self.sessionID = json.loads(response.content)['data']['sessionID']

        else:
            print(f"\nAUTH ERROR\n{response}")

    # Проверка активности сессии
    def check_session(self) -> None:
        url = 'https://api.dellin.ru/v3/auth/session_info.json'
        data = {"appKey": self.token,
                "sessionID": self.sessionID}
        json_string = json.dumps(data)
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            print(f"Check session - succesful request.\nsessionID: {data['sessionID']}\n")
        else:
            print(f"\nCHECK SESSION ERROR \nWrong ApiToken/sessionID or something went wrong\nTry again to auth\n{response}")

    # Закрытие активной сессии
    def close_session(self) -> None:
        url = 'https://api.dellin.ru/v3/auth/logout.json'
        data = {"appKey": self.token,
                "sessionID": self.sessionID}
        json_string = json.dumps(data)
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            print(f"\nLOGOUT - succesful request.\nSESSION CLOSED\n")
        else:
            print(f"\nCLOSE SESSION ERROR\nWrong ApiToken/sessionID or something went wrong\nTry again\n{response}")

    # Метод возвращает список номеров предварительных заявок от ООО Гермеон на указанную дату оформления заказов
    def get_germeon_orders(self):
        url = 'https://api.dellin.ru/v3/orders.json'
        date = input('Введите дату оформления заказа в формате ГГГГ-ММ-ДД:\n')
        data = {"appkey":config["DL_API_TOKEN"], 
                "sessionID":self.sessionID,
                "dateStart": f'{date} 00:00', # Форматы даты ГГГГ-ММ-ДД
                "dateEnd": f'{date} 23:59'
                }
        json_string = json.dumps(data)
        print('\nПолучение списка заявок от ООО Гермеон\nЗагрузка...\n\n')
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            json_dict = json.loads(response.content)
            totalPages = int(json_dict['metadata']['totalPages'])
            if totalPages > 1:
                for page in range(2, totalPages + 1):
                    data = {"appkey":config["DL_API_TOKEN"], 
                            "sessionID":self.sessionID,
                            "dateStart": f'{date } 00:00', # Форматы даты ГГГГ-ММ-ДД
                            "dateEnd": f'{date} 23:59',
                            'page': page
                            }
                    json_string = json.dumps(data)
                    response = requests.post(url, headers=self.headers, data=json_string)
                    json_dict['orders'].extend(json.loads(response.content)['orders'])
            orders_list = []

            for order in json_dict['orders']:
                if "гермеон" in order['sender']['name'].lower():
                    # Возможно понадобится возвращать список заказов с полной информацией, а не определенные ключ:значение
                    orders_list.append({"Номер заявки": order['orderId'], "Получатель": order['receiver']['name'],"Количество копий": order['freight']['places'] + 1})   
                    # Количество копий маркировок равняется количеству грузовых мест + 1
            if orders_list:
                print(f"\nGET ORDER LIST - succesful request.\n\n")
                return orders_list
            else: 
                print('На выбранную дату нет заявок от ООО Гермеон. Проверьте дату')
                self.close_session()
        else:
            print(f"\nGET ORDER LIST ERROR\nWrong ApiToken/sessionID or something went wrong\nTry again\n{response}")
            self.close_session()
        pass
    
    # Сохранение печатных форм предварительных заявок в файл в папку docsForPrint для дальнейшей печати или редактирования
    def save_preorderPage(self, list: list) -> None:
        url = 'https://api.dellin.ru/v1/customers/request/pdf.json'
        print(f'\n\nСохранение печатных форм предварительных заявок в папку {os.getcwd()}/docsForPrint\n\nЗагрузка...\n\n')
        for item in list:
            data = {"appkey": config['DL_API_TOKEN'],
                    "sessionID": self.sessionID,
                    "requestID": item['Номер заявки']}
            json_string = json.dumps(data)
            # Запрос возвращает JSON с документом в формате base64
            response = requests.post(url, headers=self.headers, data=json_string)

            if response.status_code == 200:
                filename = f'{item['Номер заявки']} - {item['Получатель'].replace('"', '')}'
                try:
                    with open(f'docsForPrint/{filename}.pdf',"wb") as f:
                            f.write(base64.b64decode(json.loads(response.content)['base64']))
                            print(f"Печатная форма заявки {filename} сохранена.\n")
                except Exception as e:
                    print(f'Ошибка - {e}')
                    self.close_session()
            else:
                print(f"\nSAVE DOC ERROR\nWrong ApiToken/sessionID or something went wrong\nTry again\n{response}")
                self.close_session()
            pass


    def print_docs(self, orders_list: list) -> None:
        # Печать документов из директории. Проверяется соответствие номера заявки с названием файла и указывается количество копий документа на печать
        directory = fr'.\docsForPrint'
        try:
            for order in orders_list: 
                for filename in os.listdir(directory):
                    if order['Номер заявки'] in filename:
                        PrintDocument.print_document(fr'{directory}\{filename}', order['Количество копий'] )
                        os.remove(fr'{directory}\{filename}')
                        print(f"Печатная форма заявки {directory}\{filename} удалена.\n")
        except Exception as e:
            print(f'In print docs:\n{e}')

        
                    

if not os.path.exists('docsForPrint'):
            os.mkdir('docsForPrint')
config = dotenv_values('.env')
app = DellinScraper(config['DL_API_TOKEN'], config['LOGIN'], config['PASSWORD'])

if not os.listdir('docsForPrint'):
    app.auth()
    app.check_session()
    orders = app.get_germeon_orders()
    if orders:
        app.save_preorderPage(orders)
        app.print_docs(orders)
        app.close_session()
else:
    print(f'Каталог не пустой')
    app.close_session()
    exit()
    # 2025-06-16





