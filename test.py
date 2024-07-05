import time

import requests
import ua_generator

# Прокси-сервер
proxies = {
    "http": "http://teiqogrk:md5yfndvjcze@45.94.47.66:8110",
    "https": "http://teiqogrk:md5yfndvjcze@45.94.47.66:8110"
}

# URL для запросов
url = "https://steamcommunity.com/inventory/76561198386116962/730/2?l=english&count=2000"
ua = ua_generator.generate().headers.get()
additional = {'Connection': 'close', 'Accept-Encoding': 'gzip, deflate, br, zstd'}
headers = ua | additional
# Счетчик запросов
request_count = 0

while True:
    try:
        # Отправка запроса
        print(f'запрос {proxies}')
        response = requests.get(url, proxies=proxies, headers=headers)

        # Увеличение счетчика запросов
        request_count += 1

        # Проверка кода состояния ответа
        if response.status_code == 429:
            print(f"Received 429 Too Many Requests after {request_count} requests")
            break

        # Ожидание 5 секунд перед следующим запросом
        time.sleep(4)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        print(f"{request_count} requests")
        break
    except KeyboardInterrupt:
        print(f"{request_count} requests")
        exit()
