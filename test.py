import asyncio



class InventoryProcessor:
    def __init__(self, proxies: list[str]):
        self.proxies = proxies

    async def process_inventory_price(self, steam_id: int, proxies: list[str]):
        # Это пример функции для обработки цены инвентаря.
        # Ваша реальная функция должна быть здесь.
        await asyncio.sleep(1)  # эмуляция задержки
        return (f"Steam ID: {steam_id}", len(proxies), sum(len(proxy) for proxy in proxies))

    async def process_inventories(self, steam_ids: list[int]) -> list[tuple[str, int, float]]:
        """
        Смотрит цену всех инвентарей.
        Args:
            steam_ids (list[int]): лист стим айди

        Returns:
            list[tuple[str, int, float]]: вернет лист с кортежом с названием, количеством, ценой.
        """
        results = []
        num_proxies = len(self.proxies)
        num_steam_ids = len(steam_ids)
        proxy_index = 0

        while steam_ids:
            tasks = []
            if num_steam_ids > num_proxies:
                # Если steam_ids больше чем прокси, распределяем прокси циклически
                for steam_id in steam_ids[:num_proxies]:
                    proxies_chunk = [self.proxies[proxy_index % num_proxies]]
                    proxy_index += 1
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids = steam_ids[num_proxies:]
            else:
                # Если прокси больше или равно количеству steam_ids, распределяем прокси равномерно
                num_proxies_per_task = num_proxies // num_steam_ids
                remainder = num_proxies % num_steam_ids

                start_index = 0
                for i, steam_id in enumerate(steam_ids):
                    count = num_proxies_per_task + (1 if i < remainder else 0)
                    proxies_chunk = self.proxies[start_index:start_index + count]
                    start_index += count
                    tasks.append(self.process_inventory_price(steam_id, proxies_chunk))
                steam_ids.clear()

            # Выполнение задач текущей порции
            results.extend(await asyncio.gather(*tasks))
            num_steam_ids = len(steam_ids)

        return results

# Пример использования
proxies = ["proxy1", "proxy2", "proxy3", "proxy4"]
steam_ids = [1, 2, 3, 4, 5, 6, 7]

processor = InventoryProcessor(proxies)
results = asyncio.run(processor.process_inventories(steam_ids))
print(results)
