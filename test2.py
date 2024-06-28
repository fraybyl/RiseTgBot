import requests
import sys


def measure_traffic(url):
    # Выполнение запроса
    response = requests.get(url,headers={'Accept-Enconding': 'br'},     proxies={
        "http": "http://teiqogrk-rotate:md5yfndvjcze@p.webshare.io:80/",
        "https": "http://teiqogrk-rotate:md5yfndvjcze@p.webshare.io:80/"
    })

    # Подсчёт размера отправленных данных
    method_size = len(response.request.method)
    url_size = len(response.request.url)
    headers_size = sum(len(k) + len(v) for k, v in response.request.headers.items())
    body_size = len(response.request.body) if response.request.body else 0
    sent_data_size = method_size + url_size + headers_size + body_size

    # Подсчёт размера полученных данных
    content_size = len(response.content)
    headers_size = sum(len(k) + len(v) for k, v in response.headers.items())
    received_data_size = content_size + headers_size

    # Суммарный трафик
    total_traffic = sent_data_size + received_data_size

    return sent_data_size, received_data_size, total_traffic


# Пример использования функции
url = 'https://steamcommunity.com/inventory/76561198852253632/730/2?l=english'
sent, received, total = measure_traffic(url)
print(f'Sent data: {sent} bytes')
print(f'Received data: {received} bytes')
print(f'Total traffic: {total} bytes')
