import json
from collections import defaultdict

class InventoryProcess:
    def __init__(self, json_data):
        self.json_data = json_data

    def parse_inventory_data(self):
        assets = self.json_data.get('assets', [])
        descriptions = self.json_data.get('descriptions', [])

        item_counts = self._collect_item_counts(assets)
        item_details = self._collect_item_details(descriptions)

        if not item_details or not item_counts:
            return None

        item_names_with_count = self._build_items_with_count(item_counts, item_details)

        return item_names_with_count if item_names_with_count else None

    @staticmethod
    def _collect_item_counts(assets):
        item_counts = defaultdict(int)
        for item in assets:
            unique_id = f"{item['classid']}_{item['instanceid']}"
            item_counts[unique_id] += 1
        return item_counts

    @staticmethod
    def _collect_item_details(descriptions):
        item_details = {}
        for desc in descriptions:
            if desc['marketable']:
                unique_id = f"{desc['classid']}_{desc['instanceid']}"
                item_details[unique_id] = {
                    'market_hash_name': desc['market_hash_name'],
                    'doppler_info': desc.get('doppler_info', 'N/A')
                }
        return item_details

    @staticmethod
    def _build_items_with_count(item_counts, item_details):
        items_with_count = []
        for uid, count in item_counts.items():
            if uid in item_details:
                items_with_count.append({
                    'name': item_details[uid]['market_hash_name'],
                    'count': count,
                })
        return items_with_count

# Загрузка данных из JSON-файла
with open('prices_v6.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Создание объекта InventoryProcess и парсинг данных
inventory_process = InventoryProcess(data)
marketable_items = inventory_process.parse_inventory_data()

# Вывод результата
if marketable_items:
    for item in marketable_items:
        print(f"Название: {item['name']}, Количество: {item['count']}, Doppler Info: {item['doppler_info']}")

# Сохранение результата в новый JSON-файл
with open('marketable_items.json', 'w', encoding='utf-8') as file:
    json.dump(marketable_items, file, ensure_ascii=False, indent=4)
