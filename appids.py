import requests
import json

# URL API
url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

# Запрос к API
response = requests.get(url)
data = response.json()

# Создание результирующего словаря
formatted_apps = {}

for app in data['applist']['apps']:
    app_key = f"App{app['appid']}"
    if app['name']:  # Проверка на наличие имени
        formatted_apps[app['name']] = {
            "appID": str(app['appid']),
            "name": app['name']
        }
    else:
        formatted_apps[app_key] = {
            "appID": str(app['appid']),
            "name": app['name']
        }

# Запись результата в файл appids.json
with open('appids.json', 'w', encoding='utf-8') as file:
    json.dump(formatted_apps, file, indent=2, ensure_ascii=False)

print("Данные успешно записаны в файл appids.json")
