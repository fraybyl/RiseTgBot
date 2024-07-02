from dataclasses import dataclass, asdict

import orjson

from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory


@dataclass
class Statistic:
    """
    Класс для хранения статистических данных.

    Attributes:
        total_accounts (int): Общее количество учетных записей.
        total_bans (int): Общее количество банов.
        total_vac (int): Общее количество VAC банов.
        total_community (int): Общее количество банов от сообщества.
        total_game_ban (int): Общее количество игровых банов.
        bans_in_last_week (int): Количество банов за последнюю неделю.
        items (int): Общее количество предметов.
        cases (int): Общее количество кейсов.
        prices (float): Общая сумма цен предметов.

    Methods:
        from_dict(cls, bans_list: list[AccountInfo], inventory_list: list[Inventory]) -> 'Statistic':
            Создает объект Statistic из списка данных об учетных записях и инвентарях.

        add_account_info(self, bans: AccountInfo) -> None:
            Добавляет информацию о банах из учетной записи.

        add_inventory_info(self, inventory: Inventory) -> None:
            Добавляет информацию о предметах из инвентаря.

        to_dict(self) -> str:
            Преобразует объект Statistic в строку JSON.

    """
    total_accounts: int = 0
    total_bans: int = 0
    total_vac: int = 0
    total_community: int = 0
    total_game_ban: int = 0
    bans_in_last_week: int = 0
    items: int = 0
    cases: int = 0
    prices: float = 0.0

    def __post_init__(self):
        self.prices = round(self.prices, 2)

    @classmethod
    def from_dict(cls, bans_list: list[AccountInfo], inventory_list: list[Inventory]):
        """
        Создает объект Statistic из списка данных об учетных записях и инвентарях.

        Args:
            bans_list (list[AccountInfo]): Список объектов AccountInfo.
            inventory_list (list[Inventory]): Список объектов Inventory.

        Returns:
            Statistic: Созданный объект Statistic.
        """
        instance = cls()
        for bans in bans_list:
            instance.add_account_info(bans)
        for inventory in inventory_list:
            instance.add_inventory_info(inventory)
        return instance

    def add_account_info(self, bans: AccountInfo):
        """
        Добавляет информацию о банах из учетной записи.

        Args:
            bans (AccountInfo): Объект AccountInfo.
        """
        self.total_bans += bans.is_banned()
        self.total_vac += bans.VACBanned
        self.total_community += bans.CommunityBanned
        self.total_game_ban += bans.NumberOfGameBans
        self.bans_in_last_week += bans.ban_in_last_week()

    def add_inventory_info(self, inventory: Inventory):
        """
        Добавляет информацию о предметах из инвентаря.

        Args:
            inventory (Inventory): Объект Inventory.
        """
        self.items += len(inventory.items)
        self.cases += inventory.total_cases()
        self.prices = round(inventory.total_price())

    def to_dict(self) -> str:
        """
        Преобразует объект Statistic в строку JSON.

        Returns:
            str: Строка JSON.
        """
        return orjson.dumps(asdict(self)).decode('utf-8')
