import requests
import json
import sys
from dotenv import dotenv_values
import os
import base64
import binascii
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
            print(f"\nLOGOUT - succesful.\nSESSION CLOSED\n")
        else:
            print(f"\nCLOSE SESSION ERROR\nWrong ApiToken/sessionID or session already closed\n{response}")

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
    def print_preorderPages(self, list: list) -> None:
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
                    with open(fr'.\docsForPrint\{filename}.pdf',"wb") as f:
                            f.write(base64.b64decode(json.loads(response.content)['base64']))
                            print(f"Файл {filename}.pdf сохранен.")
                            f.close()
                    # Печать файла сразу после сохранения с последующим удалением из директории.
                    try:        
                        PrintDocument.print_document(fr'.\docsForPrint\{filename}.pdf' , item['Количество копий'] )
                        os.remove(fr'.\docsForPrint\{filename}.pdf')
                        print(fr'Файл {filename}.pdf удален')
                    except Exception as e:
                        print(e)
                        self.close_session()
                except Exception as e:
                    print(f'Ошибка - {e}')
                    self.close_session()
            else:
                print(f"\nSAVE DOC ERROR\nWrong ApiToken/sessionID or something went wrong\nTry again\n{response}")
                self.close_session()

    def print_order(self, order_number, copies_number):
        url = 'https://api.dellin.ru/v1/customers/request/pdf.json'
        data = {"appkey": config['DL_API_TOKEN'],
                "sessionID": self.sessionID,
                "requestID": order_number}
        json_string = json.dumps(data)
        # Запрос возвращает JSON с документом в формате base64
        response = requests.post(url, headers=self.headers, data=json_string)

        if response.status_code == 200:
            filename = f'{order_number}'
            try:
                with open(fr'.\docsForPrint\{filename}.pdf',"wb") as f:
                        f.write(base64.b64decode(json.loads(response.content)['base64']))
                        print(f"Файл {filename}.pdf сохранен.")
                        f.close()
                # Печать файла сразу после сохранения с последующим удалением из директории.
                try:        
                    PrintDocument.print_document(fr'.\docsForPrint\{filename}.pdf' , copies_number)
                    os.remove(fr'.\docsForPrint\{filename}.pdf')
                    print(fr'Файл {filename}.pdf удален')
                except Exception as e:
                    print(e)
                    self.close_session()
            except Exception as e:
                print(f'Ошибка - {e}')
                os.remove(fr'.\docsForPrint\{filename}.pdf')
                self.close_session()
        else:
            print(f"\nPRINT ORDER ERR\НОМЕР ЗАЯВКИ {order_number} НЕ СУЩЕСТВУЕТ ИЛИ что-то пошло не так\nTry again\n{response}")
            self.close_session()

    # # Сейчас не используется. Метод нужен был для печати файлов только после сохранения всех заявок в запросе. 
    # def print_docs(self, orders_list: list) -> None:
    #     # Печать документов из директории. Проверяется соответствие номера заявки с названием файла и указывается количество копий документа на печать
    #     directory = fr'.\docsForPrint'
    #     try:
    #         for order in orders_list: 
    #             for filename in os.listdir(directory):
    #                 if order['Номер заявки'] in filename:
    #                     PrintDocument.print_document(fr'{directory}\{filename}', order['Количество копий'] )
    #                     os.remove(fr'{directory}\{filename}')
    #                     print(fr"Печатная форма заявки {directory}\{filename} удалена.\n")
    #     except Exception as e:
    #         print(f'In print docs:\n{e}')

        
                    

if not os.path.exists('docsForPrint'):
            os.mkdir('docsForPrint')

# обязательный кусок кода для добавления .env файла при компиляции в exe
extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
config = dotenv_values(os.path.join(extDataDir, '.env'))


app = DellinScraper(config['DL_API_TOKEN'], config['LOGIN'], config['PASSWORD'])

if not os.listdir('docsForPrint'):
    app.auth()
    app.check_session()
    mode = input('Выберите режим:\n1 - для печати всех предварительных заявок на определенную дату\n2 - для печати по номеру заявки\n')
    if int(mode)==1:
        orders = app.get_germeon_orders()
        if orders:
            app.print_preorderPages(orders)
            app.close_session()
    elif int(mode)==2: 
        order_number = input("Введите номер заявки:\n")
        copies_number = input("Введите количество копий документа для печати:\n")
        app.print_order(order_number, copies_number)
        app.close_session()
    else:
        print("Неправильно указан режим")
        app.close_session()
else:
    print(f'Каталог не пустой')
    app.close_session()
    exit()
    # 2025-07-23





